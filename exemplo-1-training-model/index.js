import tf from '@tensorflow/tfjs-node';

// Exemplo de pessoas para treino (cada pessoa com idade, cor e localização)
// const pessoas = [
//     { nome: "Erick", idade: 30, cor: "azul", localizacao: "São Paulo" },
//     { nome: "Ana", idade: 25, cor: "vermelho", localizacao: "Rio" },
//     { nome: "Carlos", idade: 40, cor: "verde", localizacao: "Curitiba" }
// ];

// Vetores de entrada com valores já normalizados e one-hot encoded
// Ordem: [idade_normalizada, azul, vermelho, verde, São Paulo, Rio, Curitiba]
// const tensorPessoas = [
//     [0.33, 1, 0, 0, 1, 0, 0], // Erick
//     [0, 0, 1, 0, 0, 1, 0],    // Ana
//     [1, 0, 0, 1, 0, 0, 1]     // Carlos
// ]

// Usamos apenas os dados numéricos, como a rede neural só entende números.
// tensorPessoasNormalizado corresponde ao dataset de entrada do modelo.
const tensorPessoasNormalizado = [
    [0.33, 1, 0, 0, 1, 0, 0], // Erick
    [0, 0, 1, 0, 0, 1, 0],    // Ana
    [1, 0, 0, 1, 0, 0, 1]     // Carlos
]

// Labels das categorias a serem previstas (one-hot encoded)
// [premium, medium, basic]
const labelsNomes = ["premium", "medium", "basic"]; // Ordem dos labels
const tensorLabels = [
    [1, 0, 0], // premium - Erick
    [0, 1, 0], // medium - Ana
    [0, 0, 1]  // basic - Carlos
];

// Criamos tensores de entrada (xs) e saída (ys) para treinar o modelo
const inputXs = tf.tensor2d(tensorPessoasNormalizado)
const outputYs = tf.tensor2d(tensorLabels)

inputXs.print();
outputYs.print();

const model = await trainModel(inputXs, outputYs);
const pessoa = {nome: "Ze", idade: 28, cor: "vermelho", localizacao: "Curitiba"};

const pessoaNormalizada = [
    pessoa.idade / 100, 
    pessoa.cor === "azul" ? 1 : 0, 
    pessoa.cor === "vermelho" ? 1 : 0, 
    pessoa.cor === "verde" ? 1 : 0, 
    pessoa.localizacao === "São Paulo" ? 1 : 0, 
    pessoa.localizacao === "Rio" ? 1 : 0, 
    pessoa.localizacao === "Curitiba" ? 1 : 0
];

const predictions = await predict(model, pessoaNormalizada);

const sortedPredictions = predictions.sort((a, b) => b.prob - a.prob);
console.log('Predições ordenadas:');
console.log(sortedPredictions);

console.log(`${pessoa.nome} é ${labelsNomes[sortedPredictions[0].index]}`);
console.log(`Probabilidade: ${sortedPredictions[0].prob}`);


async function trainModel(inputXs, outputYs) {
    
    console.log('Criando modelo...');
    const model = tf.sequential();
    console.log('Adicionando camadas...');
    model.add(tf.layers.dense({units: 80, inputShape: [7], activation: 'relu'}));
    console.log('Adicionando camada de saída...');
    model.add(tf.layers.dense({units: 3, activation: 'softmax'}));
    console.log('Compilando modelo...');
    model.compile({optimizer: 'adam', loss: 'categoricalCrossentropy', metrics: ['accuracy']});

    console.log('Iniciando treinamento...');
    await model.fit(inputXs, outputYs, 
        {
            epochs: 100,
            shuffle: true,
            batchSize: 10,
            verbose: 0, callbacks: {
                onEpochEnd: async (epoch, logs) => {
                    // console.log(`Epoch ${epoch} - Loss: ${logs.loss}`);
                }
            }   
        });

    return model;
}

async function predict(model, pessoa) {

    const inputXs = tf.tensor2d([pessoa]);
    console.log('Predizendo...');
    const predictions = model.predict(inputXs); 
    const predictionsArray = await predictions.array();
    console.log('Predições:');
    return predictionsArray[0].map((prob, index) => ({prob, index}));
}