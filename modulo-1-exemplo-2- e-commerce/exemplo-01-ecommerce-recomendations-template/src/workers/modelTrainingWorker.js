import 'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js';
import { workerEvents } from '../events/constants.js';

// Força o TensorFlow.js a usar o backend CPU em vez de WebGL (GPU)
await tf.setBackend('cpu');
await tf.ready();

console.log('Model training worker initialized');
let _globalCtx = {};

function oneHotEncode(value, uniqueValues) {
    return uniqueValues.map(v => v === value ? 1 : 0);
}

function encodeProduct(product, categories, colors, genders, minPrice, maxPrice) {
    return [
        ...oneHotEncode(product.category, categories),
        ...oneHotEncode(product.color, colors),
        ...oneHotEncode(product.sexo || 'unissex', genders),
        (product.price - minPrice) / (maxPrice - minPrice)
    ];
}

function normalizeAge(age, minAge, maxAge) {
    return (age - minAge) / (maxAge - minAge);
}

// Peso de afinidade entre sexo do usuário e sexo do produto
// 1 = mesmo sexo, 0 = produto unissex, -1 = sexo oposto
function genderMatchWeight(userSexo, productSexo) {
    const uSexo = userSexo || 'unissex';
    const pSexo = productSexo || 'unissex';
    if (pSexo === 'unissex') return 0;
    return uSexo === pSexo ? 1 : -1;
}

async function makeContext(catalog, users) {
    const categories = [...new Set(catalog.map(p => p.category))];
    const colors = [...new Set(catalog.map(p => p.color))];
    const productGenders = [...new Set(catalog.map(p => p.sexo || 'unissex'))];
    const userGenders = [...new Set(users.map(u => u.sexo || 'unissex'))];
    const minPrice = Math.min(...catalog.map(p => p.price));
    const maxPrice = Math.max(...catalog.map(p => p.price));
    const minAge = Math.min(...users.map(u => u.age));
    const maxAge = Math.max(...users.map(u => u.age));
    // features: produto (category + color + sexo + preço) + idade + sexo usuário + peso afinidade gênero
    const featureSize = categories.length + colors.length + productGenders.length + 1 + 1 + userGenders.length + 1;

    const productFeatures = {};
    catalog.forEach(p => {
        productFeatures[p.id] = encodeProduct(p, categories, colors, productGenders, minPrice, maxPrice);
    });

    const trainingData = [];
    users.forEach(user => {
        const ageNorm = normalizeAge(user.age, minAge, maxAge);
        const userGenderEncoded = oneHotEncode(user.sexo || 'unissex', userGenders);
        const purchasedIds = new Set(user.purchases.map(p => p.id));
        catalog.forEach(product => {
            const genderWeight = genderMatchWeight(user.sexo, product.sexo);
            trainingData.push({
                features: [genderWeight, ...productFeatures[product.id], ageNorm, ...userGenderEncoded],
                label: purchasedIds.has(product.id) ? 1 : 0
            });
        });
    });

    return {
        catalog,
        categories,
        colors,
        productGenders,
        userGenders,
        minPrice,
        maxPrice,
        minAge,
        maxAge,
        featureSize,
        productFeatures,
        trainingData,
    };
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

let _epochCounter = 0;

async function trainModel({ users }) {
    console.log('Training model with users:', users);

    // Notifica a interface que o treino iniciou (barra de progresso em 10%)
    postMessage({ type: workerEvents.progressUpdate, progress: { progress: 10 } });

    try {
        // Busca o catálogo completo de produtos do servidor
        const catalog = await (await fetch('/data/products.json')).json();
        // Monta o contexto: codifica produtos e usuários em vetores numéricos para a rede neural
        const ctx = await makeContext(catalog, users);
        console.log('ctx', ctx);
        // Separa amostras positivas (comprou) e negativas (não comprou)
        const positives = ctx.trainingData.filter(d => d.label === 1);
        const negatives = ctx.trainingData.filter(d => d.label === 0);

        // Oversampling: duplica as amostras positivas até equilibrar com as negativas
        const oversampled = [...negatives];
        while (oversampled.filter(d => d.label === 1).length < negatives.length) {
            oversampled.push(...positives);
        }

        // Embaralha os dados para evitar que o modelo aprenda padrões baseados na ordem
        const shuffled = shuffle(oversampled);

        // Cria o modelo apenas na primeira execução; nas seguintes, reutiliza o existente
        if (!_globalCtx.model) {
            // Modelo sequencial: camadas empilhadas uma após a outra
            const model = tf.sequential();
            // 1ª camada oculta: 2x o tamanho da entrada, relu ativa apenas valores positivos, L2 penaliza pesos grandes
            model.add(tf.layers.dense({
                units: ctx.featureSize * 2,
                activation: 'relu',
                kernelRegularizer: tf.regularizers.l2({ l2: 0.001 }),
                inputShape: [ctx.featureSize]
            }));
            // Dropout 30%: desliga neurônios aleatórios durante o treino para evitar overfitting
            model.add(tf.layers.dropout({ rate: 0.3 }));
            // 2ª camada oculta: reduz para o tamanho da entrada, continua com relu e L2
            model.add(tf.layers.dense({
                units: Math.ceil(ctx.featureSize),
                activation: 'relu',
                kernelRegularizer: tf.regularizers.l2({ l2: 0.001 })
            }));
            // Dropout 20%: regularização mais leve conforme a rede afunila
            model.add(tf.layers.dropout({ rate: 0.2 }));
            // 3ª camada oculta: metade do tamanho da entrada, afunila antes da saída
            model.add(tf.layers.dense({
                units: Math.ceil(ctx.featureSize / 2),
                activation: 'relu'
            }));
            // Camada de saída: 1 neurônio com sigmoid — retorna probabilidade entre 0 e 1 (compra ou não)
            model.add(tf.layers.dense({ units: 1, activation: 'sigmoid' }));
            // Compila: Adam com lr=0.001 (padrão estável), loss binária para sim/não, métrica de acurácia
            model.compile({
                optimizer: tf.train.adam(0.001),
                loss: 'binaryCrossentropy',
                metrics: ['accuracy']
            });
            // Salva o modelo e contexto globalmente para reuso entre chamadas
            _globalCtx = { ...ctx, model };
            // Reseta o contador de épocas para a primeira execução
            _epochCounter = 0;
        } else {
            // Reutiliza o modelo existente mas atualiza o contexto (dados podem ter mudado)
            _globalCtx = { ...ctx, model: _globalCtx.model };
        }

        // Converte features (entrada) em tensor 2D — cada linha é um par [produto, usuário] codificado
        const xs = tf.tensor2d(shuffled.map(d => d.features));
        // Converte labels (saída esperada) em tensor 2D — 1 se comprou, 0 se não
        const ys = tf.tensor2d(shuffled.map(d => [d.label]));

        // Treina 10 épocas por clique — cada época percorre todos os dados uma vez
        const epochsPerRun = 10;
        await _globalCtx.model.fit(xs, ys, {
            epochs: epochsPerRun,
            // Processa 32 amostras por vez antes de atualizar os pesos da rede
            batchSize: 32,
            callbacks: {
                // Executado ao final de cada época — envia métricas para os gráficos
                onEpochEnd: (epoch, logs) => {
                    // Incrementa o contador global para manter continuidade entre cliques
                    _epochCounter++;
                    // Envia loss (erro) e accuracy (acerto) para atualizar os gráficos em tempo real
                    postMessage({
                        type: workerEvents.trainingLog,
                        epoch: _epochCounter,
                        loss: logs.loss,
                        accuracy: logs.acc
                    });
                    // Calcula e envia o progresso percentual desta rodada de treino
                    const progress = Math.round(((epoch + 1) / epochsPerRun) * 100);
                    postMessage({ type: workerEvents.progressUpdate, progress: { progress } });
                }
            }
        });

        // Libera memória dos tensores — evita vazamento de memória na CPU
        xs.dispose();
        ys.dispose();
    } catch (error) {
        console.error('Training failed:', error);
        console.error('Stack trace:', error.stack);
        console.error('Error message:', error.message);
    } finally {
        // Garante que o botão sempre reseta, mesmo em caso de erro
        postMessage({ type: workerEvents.progressUpdate, progress: { progress: 100 } });
        postMessage({ type: workerEvents.trainingComplete });
    }
}

function recommend(user, ctx) {
    console.log('will recommend for user:', user);
    const { model, catalog, productFeatures, minAge, maxAge, userGenders } = ctx;

    if (!model) {
        postMessage({ type: workerEvents.recommend, user, recommendations: [] });
        return;
    }

    const purchasedIds = new Set(user.purchases.map(p => p.id));
    const unpurchased = catalog.filter(p => !purchasedIds.has(p.id));

    if (unpurchased.length === 0) {
        postMessage({ type: workerEvents.recommend, user, recommendations: [] });
        return;
    }

    const ageNorm = normalizeAge(user.age, minAge, maxAge);
    const userGenderEncoded = oneHotEncode(user.sexo || 'unissex', userGenders);
    const features = unpurchased.map(p => {
        const genderWeight = genderMatchWeight(user.sexo, p.sexo);
        return [genderWeight, ...productFeatures[p.id], ageNorm, ...userGenderEncoded];
    });
    const input = tf.tensor2d(features);
    const scores = model.predict(input);
    const scoresArray = scores.dataSync();

    input.dispose();
    scores.dispose();

    const scored = unpurchased.map((product, i) => ({
        ...product,
        score: scoresArray[i]
    }));
    scored.sort((a, b) => b.score - a.score);

    postMessage({
        type: workerEvents.recommend,
        user,
        recommendations: scored
    });
}


const handlers = {
    [workerEvents.trainModel]: trainModel,
    [workerEvents.recommend]: d => recommend(d.user, _globalCtx),
};

self.onmessage = async (e) => {
    const { action, ...data } = e.data;
    if (handlers[action]) {
        try {
            await handlers[action](data);
        } catch (error) {
            console.error(`Worker handler error [${action}]:`, error);
        }
    }
};
