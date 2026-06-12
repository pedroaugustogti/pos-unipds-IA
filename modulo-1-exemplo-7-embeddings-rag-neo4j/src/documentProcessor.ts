import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf"
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter'
import { Document } from "@langchain/core/documents"
import { type TextSplitterConfig } from './config.ts'

export interface ImageIdentityConfig {
  path: string
  personName: string
  email: string
}

export class DocumentProcessor {
  private pdfPath: string
  private textSplitterConfig: TextSplitterConfig
  private imageConfig?: ImageIdentityConfig

  constructor(
    pdfPath: string,
    textSplitterConfig: TextSplitterConfig,
    imageConfig?: ImageIdentityConfig,
  ) {
    this.pdfPath = pdfPath
    this.textSplitterConfig = textSplitterConfig
    this.imageConfig = imageConfig
  }

  /**
   * Chunks de texto que associam o arquivo de imagem à pessoa (embeddings são só de texto;
   * não há visão computacional aqui).
   */
  buildImageIdentityChunks(): Document[] {
    if (!this.imageConfig) {
      return []
    }
    const { path: imagePath, personName, email } = this.imageConfig
    const fileName = imagePath.replace(/^.*[/\\]/, "")
    const respostaFoto = `${personName}, seu contato pessoal é ${email}`
    const lines = [
      `Quem é essa pessoa da foto? ${respostaFoto}.`,
      `Pergunta: quem é essa pessoa da foto? Resposta: ${respostaFoto}.`,
      `${respostaFoto}. Esta informação refere-se à imagem ${fileName}.`,
      `A imagem armazenada em ${fileName} (caminho: ${imagePath}) retrata ${personName}. Contato: ${email}.`,
      `Esta fotografia identifica visualmente ${personName} (${email}). O arquivo da imagem é ${fileName}.`,
      `Quem aparece na foto ${fileName} é ${personName}. E-mail: ${email}.`,
      `${personName} (${email}) é a pessoa mostrada na imagem de perfil ${fileName}.`,
      `Metadados da imagem: arquivo ${imagePath}; pessoa retratada: ${personName}; e-mail: ${email}.`,
      `Para consultas sobre a foto ou sobre quem é essa pessoa: trata-se de ${personName} (${email}), imagem ${fileName}.`,
    ]
    return lines.map((pageContent, chunkIndex) => new Document({
      pageContent,
      metadata: {
        source: imagePath,
        type: "image",
        personName,
        email,
        chunkIndex: String(chunkIndex),
      },
    }))
  }

  async loadAndSplit() {
    const loader = new PDFLoader(this.pdfPath)
    const rawDocuments = await loader.load()
    console.log(`📄 Loaded ${rawDocuments.length} pages from PDF`);

    const splitter = new RecursiveCharacterTextSplitter(
      this.textSplitterConfig
    )
    const documents = await splitter.splitDocuments(rawDocuments)
    console.log(`✂️ Split into ${documents.length} chunks`);

    return documents.map(doc => ({
      ...doc,
      metadata: {
        source: doc.metadata.source,
      }
    }))
  }
}
