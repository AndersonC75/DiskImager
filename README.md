# Pendrive/SD Card Imager for Windows (Python GUI)

(English Version Below)

## Descrição Curta

Uma ferramenta gráfica simples para Windows, criada em Python, que permite criar imagens de disco brutas (arquivos `.img`) a partir de pendrives USB e cartões MicroSD. Ideal para backups completos ou para duplicar dispositivos.

![Diskimager](https://github.com/user-attachments/assets/a3626c35-b8a1-4a49-9a52-525d2df261db)

## ✨ Funcionalidades

*   **Interface Gráfica Simples:** Fácil de usar através do Tkinter.
*   **Listagem Automática de Discos:** Detecta discos físicos removíveis (e outros) usando WMIC.
*   **Seleção Segura:** Permite selecionar visualmente a unidade de origem e o arquivo de destino.
*   **Criação de Imagem Bruta:** Gera uma cópia byte-a-byte do dispositivo selecionado (formato `.img`).
*   **Barra de Progresso:** Mostra o andamento da criação da imagem.
*   **Requer Admin:** Solicita automaticamente permissões de Administrador (via UAC) para acesso direto ao disco.
*   **Portátil:** Pode ser compilado em um único arquivo `.exe` usando PyInstaller.

## ⚠️ Avisos Importantes

*   **EXECUTE COMO ADMINISTRADOR:** O programa **precisa** ser executado com privilégios de Administrador para funcionar corretamente. O `.exe` compilado com a opção `--uac-admin` solicitará isso automaticamente.
*   **SELECIONE A UNIDADE DE ORIGEM CORRETA:** **Verifique com MUITO CUIDADO** qual disco você seleciona como origem. Criar uma imagem do disco errado (como seu C:) não causará perda de dados *neste programa* (pois ele só lê), mas é uma perda de tempo e pode gerar um arquivo inútil e enorme. Use o tamanho e o modelo do disco como guia.
*   **IMAGEM BRUTA (.img), NÃO .iso:** Este programa cria uma imagem de disco completa, setor por setor. Não é um arquivo `.iso` no formato de CD/DVD (ISO 9660).
*   **USO POR SUA CONTA E RISCO:** Embora testado, use este software com cautela. O autor não se responsabiliza por perda de tempo ou problemas decorrentes do uso incorreto.

## 🚀 Como Usar (Usuários Finais)

1.  Vá para a seção [**Releases**](https://github.com/SEU_USUARIO/SEU_REPOSITORIO/releases) deste repositório.
2.  Baixe o arquivo `DiskImager.exe` da versão mais recente.
3.  Execute o `DiskImager.exe`. O Windows solicitará permissão de Administrador (UAC) - **aceite**.
4.  A interface gráfica será aberta. Use "Atualizar Lista" se necessário.
5.  Selecione o pendrive ou cartão SD correto na lista de "Disco de Origem". **Verifique duas vezes!**
6.  Clique em "Procurar..." para escolher onde salvar o arquivo `.img` e qual nome dar a ele.
7.  Clique em "Criar Imagem".
8.  Leia a confirmação final com **atenção** e clique em "Sim" se tiver certeza.
9.  Aguarde a barra de progresso completar.
10. O arquivo `.img` estará pronto no local escolhido.

## 🛠️ Como Compilar (Desenvolvedores)

Se você quiser modificar o código ou compilá-lo você mesmo:

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
    cd SEU_REPOSITORIO
    ```
2.  **Instale Python:** Certifique-se de ter o [Python 3.x](https://www.python.org/) instalado e adicionado ao PATH.
3.  **(Recomendado) Crie um Ambiente Virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Instale as Dependências:** A única dependência externa para compilar é o PyInstaller. O Tkinter já vem com o Python.
    ```bash
    pip install pyinstaller
    ```
5.  **Execute o PyInstaller:** Use o comando que funcionou para você (provavelmente o último teste):
    ```bash
    pyinstaller --windowed --uac-admin --name DiskImager --icon=disk.ico gui_disk_imager.py
    ```
    *(Certifique-se que `gui_disk_imager.py` é o nome do seu arquivo principal e `disk.ico` existe ou remova a opção `--icon`)*
6.  O executável `DiskImager.exe` estará na pasta `dist`.

## 💻 Tecnologias Utilizadas

*   [Python 3](https://www.python.org/)
*   [Tkinter](https://docs.python.org/3/library/tkinter.html) (para a GUI)
*   [subprocess](https://docs.python.org/3/library/subprocess.html) (para chamar `wmic`)
*   [PyInstaller](https://pyinstaller.org/) (para criar o `.exe`)

## 📄 Licença

Este projeto é distribuído sob a licença [NOME DA LICENÇA, ex: MIT]. Veja o arquivo `LICENSE` para mais detalhes.
*(**Ação:** Escolha uma licença - MIT é uma boa opção padrão - e adicione um arquivo `LICENSE` ao seu repositório)*

---

# Pendrive/SD Card Imager for Windows (Python GUI) - English Version

## Short Description

A simple graphical tool for Windows, built with Python, that allows creating raw disk images (`.img` files) from USB flash drives and MicroSD cards. Ideal for full backups or device duplication.

## 🖼️ Screenshot

[INSERT SCREENSHOT OF THE GUI HERE]
*You can take a screenshot of the program window, upload it to the repository, and reference the link here. Ex: ![GUI Screenshot](screenshot.png)*

## ✨ Features

*   **Simple Graphical Interface:** Easy to use via Tkinter.
*   **Automatic Disk Listing:** Detects removable (and other) physical disks using WMIC.
*   **Safe Selection:** Allows visually selecting the source drive and the destination file.
*   **Raw Image Creation:** Generates a byte-by-byte copy of the selected device (`.img` format).
*   **Progress Bar:** Shows the progress of the image creation.
*   **Admin Required:** Automatically requests Administrator permissions (via UAC) for direct disk access.
*   **Portable:** Can be compiled into a single `.exe` file using PyInstaller.

## ⚠️ Important Warnings

*   **RUN AS ADMINISTRATOR:** The program **must** be run with Administrator privileges to function correctly. The `.exe` compiled with the `--uac-admin` option will request this automatically.
*   **SELECT THE CORRECT SOURCE DRIVE:** **Double-check VERY CAREFULLY** which disk you select as the source. Creating an image of the wrong disk (like your C: drive) won't cause data loss *with this program* (as it only reads), but it's a waste of time and can generate a useless, huge file. Use the disk size and model as a guide.
*   **RAW IMAGE (.img), NOT .iso:** This program creates a full, sector-by-sector disk image. It is not an `.iso` file in the CD/DVD format (ISO 9660).
*   **USE AT YOUR OWN RISK:** Although tested, use this software with caution. The author is not responsible for wasted time or issues arising from incorrect use.

## 🚀 How to Use (End Users)

1.  Go to the [**Releases**](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/releases) section of this repository.
2.  Download the `DiskImager.exe` file from the latest release.
3.  Run `DiskImager.exe`. Windows will ask for Administrator permission (UAC) - **accept it**.
4.  The graphical interface will open. Use "Refresh List" if needed.
5.  Select the correct flash drive or SD card from the "Source Disk" list. **Double-check!**
6.  Click "Browse..." to choose where to save the `.img` file and what name to give it.
7.  Click "Create Image".
8.  Read the final confirmation prompt **carefully** and click "Yes" if you are sure.
9.  Wait for the progress bar to complete.
10. The `.img` file will be ready in the chosen location.

## 🛠️ How to Build (Developers)

If you want to modify the code or build it yourself:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY
    ```
2.  **Install Python:** Make sure you have [Python 3.x](https://www.python.org/) installed and added to your PATH.
3.  **(Recommended) Create a Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Install Dependencies:** The only external dependency for building is PyInstaller. Tkinter comes with Python.
    ```bash
    pip install pyinstaller
    ```
5.  **Run PyInstaller:** Use the command that worked for you (likely the last test):
    ```bash
    pyinstaller --windowed --uac-admin --name DiskImager --icon=disk.ico gui_disk_imager.py
    ```
    *(Make sure `gui_disk_imager.py` is your main script file name and `disk.ico` exists, or remove the `--icon` option)*
6.  The `DiskImager.exe` executable will be in the `dist` folder.

## 💻 Technology Stack

*   [Python 3](https://www.python.org/)
*   [Tkinter](https://docs.python.org/3/library/tkinter.html) (for the GUI)
*   [subprocess](https://docs.python.org/3/library/subprocess.html) (to call `wmic`)
*   [PyInstaller](https://pyinstaller.org/) (to create the `.exe`)

## 📄 License

This project is distributed under the [LICENSE NAME, e.g., MIT] License. See the `LICENSE` file for more details.
*(**Action:** Choose a license - MIT is a good default choice - and add a `LICENSE` file to your repository)*"# DiskImager" 
