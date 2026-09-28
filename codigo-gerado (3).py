import streamlit as st
import subprocess
import os
import fitz  # PyMuPDF (instalado via pymupdf no requirements.txt)
import tempfile

# Configuração da interface
st.set_page_config(page_title="Conversor PDF/A Societário", page_icon="📄")

class ConversorPDFA:
    def __init__(self):
        # No Streamlit Cloud (Linux), o comando do Ghostscript é apenas 'gs'
        self.gs_cmd = "gs"

    def converter(self, input_path, output_path):
        """Converte para PDF/A-2b usando Ghostscript"""
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
            return False, f"Erro no motor de conversão: {e.stderr}"
        except FileNotFoundError:
            return False, "Ghostscript não instalado no servidor. Verifique o arquivo packages.txt."

    def validar(self, file_path):
        """Valida se o arquivo tem metadados PDF/A"""
        try:
            doc = fitz.open(file_path)
            metadata = str(doc.metadata).lower()
            # Verifica se existem tags de identificação PDF/A
            is_pdfa = "pdfaid" in metadata or "pdfa" in metadata
            doc.close()
            return is_pdfa
        except Exception as e:
            return False

# --- Interface Streamlit ---
st.title("📄 Conversor PDF/A para Legalização")
st.subheader("Padrão aceito por Juntas Comerciais e órgãos públicos")

arquivo = st.file_uploader("Envie seu PDF normal", type=["pdf"])

if arquivo:
    if st.button("Gerar PDF/A"):
        with st.spinner("Convertendo..."):
            # Criação de arquivos temporários seguros
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                tmp_in.write(arquivo.getvalue())
                path_in = tmp_in.name
            
            path_out = path_in.replace(".pdf", "_final.pdf")
            
            conv = ConversorPDFA()
            sucesso, msg_erro = conv.converter(path_in, path_out)
            
            if sucesso:
                if conv.validar(path_out):
                    st.success("✅ Arquivo convertido e validado com sucesso!")
                    with open(path_out, "rb") as f:
                        st.download_button(
                            label="📥 Baixar Arquivo PDF/A",
                            data=f,
                            file_name=f"{arquivo.name.replace('.pdf', '')}_PDFA.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.warning("⚠️ Arquivo gerado, mas a tag de metadados PDF/A não foi detectada. Verifique a integridade do original.")
            else:
                st.error(f"❌ Erro: {msg_erro}")
            
            # Limpeza
            if os.path.exists(path_in): os.remove(path_in)
            if os.path.exists(path_out): os.remove(path_out)

st.markdown("---")
st.caption("Desenvolvido para conformidade no setor societário e contábil.")