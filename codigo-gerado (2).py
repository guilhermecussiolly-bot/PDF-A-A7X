import streamlit as st
import subprocess
import os
import fitz  # PyMuPDF
import tempfile

# Configuração da Página
st.set_page_config(page_title="Conversor PDF/A Online", page_icon="📄")

class ConversorWeb:
    def __init__(self):
        self.gs_cmd = "gs" # Comando padrão no Linux/Cloud

    def converter_para_pdfa(self, input_path, output_path):
        """Converte PDF para PDF/A-2b usando Ghostscript"""
        comando = [
            self.gs_cmd,
            "-dPDFA",
            "-dBATCH",
            "-dNOPAUSE",
            "-dNOOUTERSAVE",
            "-sProcessColorModel=DeviceRGB",
            "-sDEVICE=pdfwrite",
            "-dPDFACompatibilityPolicy=1",
            f"-sOutputFile={output_path}",
            input_path
        ]
        
        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
            return True, ""
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def validar_pdfa(self, file_path):
        """Valida integridade e metadados"""
        try:
            doc = fitz.open(file_path)
            metadata = str(doc.metadata).lower()
            is_valid = doc.page_count > 0
            is_pdfa = "pdfaid" in metadata or "pdfa" in metadata
            doc.close()
            return is_valid and is_pdfa
        except:
            return False

# --- Interface do Usuário ---
st.title("📄 Conversor PDF para PDF/A")
st.markdown("Transforme seus documentos para o padrão de arquivamento digital de forma segura.")

arquivo_upload = st.file_uploader("Escolha um arquivo PDF", type=["pdf"])

if arquivo_upload is not None:
    if st.button("Converter Agora"):
        with st.spinner("Processando conversão..."):
            # Criar arquivos temporários para processamento
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                tmp_in.write(arquivo_upload.getvalue())
                path_in = tmp_in.name
            
            path_out = path_in.replace(".pdf", "_pdfa.pdf")
            
            conversor = ConversorWeb()
            sucesso, erro = conversor.converter_para_pdfa(path_in, path_out)
            
            if sucesso:
                if conversor.validar_pdfa(path_out):
                    st.success("✅ Conversão bem-sucedida e validada!")
                    
                    with open(path_out, "rb") as f:
                        st.download_button(
                            label="📥 Baixar PDF/A",
                            data=f,
                            file_name=f"{arquivo_upload.name.replace('.pdf', '')}_PDFA.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.warning("⚠️ Arquivo gerado, mas a validação de metadados PDF/A falhou.")
            else:
                st.error(f"❌ Erro na conversão: {erro}")
            
            # Limpeza de arquivos temporários
            if os.path.exists(path_in): os.remove(path_in)
            if os.path.exists(path_out): os.remove(path_out)

st.info("Nota: Este conversor utiliza Ghostscript para garantir a conformidade técnica exigida por órgãos públicos.")