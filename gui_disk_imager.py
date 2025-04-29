import sys
import os
import subprocess
import ctypes
import threading
import io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- Funções de Backend (Ligeiramente adaptadas para GUI) ---

def is_admin():
    """Verifica se o script está sendo executado com privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def list_disks_windows():
    """Lista discos físicos no Windows usando WMIC. Retorna lista de dicionários."""
    disks_info = []
    try:
        proc = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'DeviceID,Model,Size,Index,MediaType,InterfaceType', '/format:csv'],
            capture_output=True, text=True, check=True, encoding='cp850', errors='ignore',
            creationflags=subprocess.CREATE_NO_WINDOW # Não mostrar janela do console do wmic
        )
        output = proc.stdout.strip()
        lines = output.splitlines()
        if len(lines) <= 1: return []

        header = lines[0].split(',')
        try:
            idx_devid = header.index('DeviceID')
            idx_index = header.index('Index')
            idx_model = header.index('Model')
            idx_size = header.index('Size')
            idx_media = header.index('MediaType')
            idx_iface = header.index('InterfaceType')
        except ValueError:
            print("Erro: Coluna esperada não encontrada no cabeçalho WMIC.")
            return [] # Retorna lista vazia em caso de erro

        for line in lines[1:]:
            if not line.strip(): continue
            parts = line.split(',')
            if len(parts) <= max(idx_devid, idx_index, idx_model, idx_size, idx_media, idx_iface): continue

            device_id = parts[idx_devid].strip()
            model = parts[idx_model].strip()
            size_str = parts[idx_size].strip()
            index_str = parts[idx_index].strip()
            media_type = parts[idx_media].strip() if idx_media < len(parts) else "N/A"
            interface = parts[idx_iface].strip() if idx_iface < len(parts) else "N/A"

            if not device_id or not size_str or not index_str: continue

            try:
                size_bytes = int(size_str)
                size_gb = size_bytes / (1024**3)
                size_formatted = f"{size_gb:.2f} GB"
                disk_index = int(index_str)
            except ValueError:
                size_bytes = 0
                size_formatted = "Inválido"
                disk_index = -1 # Índice inválido

            is_likely_removable = "Removable Media" in media_type or "USB" in interface

            disks_info.append({
                "device_id": device_id, # Ex: \\.\PhysicalDrive1
                "model": model,
                "size_bytes": size_bytes,
                "size_formatted": size_formatted,
                "index": disk_index, # Ex: 1
                "display_text": f"Disk {disk_index}: {model} ({size_formatted}) - {interface}",
                "likely_removable": is_likely_removable
            })

    except FileNotFoundError:
        messagebox.showerror("Erro", "Comando 'wmic' não encontrado. Verifique a instalação do Windows.")
        return []
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erro WMIC", f"Erro ao executar wmic: {e}")
        return []
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Erro ao listar discos: {e}")
        return []

    # Ordena por índice do disco
    disks_info.sort(key=lambda x: x['index'])
    return disks_info

def create_image_worker(source_disk_path, output_file_path, disk_size_bytes, progress_callback, status_callback):
    """Worker thread para criar a imagem, chamando callbacks para atualizar a GUI."""
    try:
        status_callback(f"Iniciando: {os.path.basename(source_disk_path)} -> {os.path.basename(output_file_path)}")
        buffer_size = io.DEFAULT_BUFFER_SIZE * 64 # Buffer maior pode ajudar na velocidade
        bytes_copied = 0

        with open(source_disk_path, 'rb') as source_disk:
            with open(output_file_path, 'wb') as output_file:
                while True:
                    chunk = source_disk.read(buffer_size)
                    if not chunk:
                        break
                    output_file.write(chunk)
                    bytes_copied += len(chunk)
                    progress = int((bytes_copied / disk_size_bytes) * 100)
                    progress_callback(progress) # Atualiza progresso

        # Garante que a barra chegue a 100% no final
        progress_callback(100)
        status_callback(f"Sucesso! Imagem '{os.path.basename(output_file_path)}' criada.")
        return True

    except PermissionError:
        status_callback(f"Erro: Permissão negada para acessar '{source_disk_path}'. Execute como Administrador!")
        return False
    except FileNotFoundError:
         status_callback(f"Erro: Arquivo/Dispositivo não encontrado. '{source_disk_path}' ou '{output_file_path}'")
         return False
    except OSError as e:
        status_callback(f"Erro de SO: {e}. (Disco pode ter sido removido?)")
        return False
    except Exception as e:
        status_callback(f"Erro inesperado na cópia: {e}")
        return False

# --- Classe da Aplicação GUI ---

class DiskImagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Criador de Imagem de Disco (Pendrive/SD)")
        self.root.geometry("600x450") # Tamanho inicial

        self.disks = []
        self.selected_disk_info = None
        self.output_file_path = tk.StringVar()

        # --- Estilo ttk ---
        style = ttk.Style()
        style.theme_use('vista') # Ou 'xpnative', 'clam', etc.

        # --- Frame Principal ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seleção de Disco de Origem ---
        source_frame = ttk.LabelFrame(main_frame, text="1. Selecione o Disco de Origem (Pendrive/Cartão SD)", padding="10")
        source_frame.pack(fill=tk.X, pady=5)

        self.disk_listbox = tk.Listbox(source_frame, height=6, exportselection=False)
        self.disk_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.disk_listbox.bind('<<ListboxSelect>>', self.on_disk_select)

        scrollbar = ttk.Scrollbar(source_frame, orient=tk.VERTICAL, command=self.disk_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.disk_listbox.config(yscrollcommand=scrollbar.set)

        refresh_button = ttk.Button(source_frame, text="Atualizar Lista", command=self.refresh_disk_list)
        refresh_button.pack(side=tk.LEFT, padx=(10,0)) # Coloca o botão à direita da listbox

        # --- Seleção de Arquivo de Destino ---
        dest_frame = ttk.LabelFrame(main_frame, text="2. Escolha o Arquivo de Imagem de Saída (.img)", padding="10")
        dest_frame.pack(fill=tk.X, pady=5)

        dest_entry = ttk.Entry(dest_frame, textvariable=self.output_file_path, width=60)
        dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_button = ttk.Button(dest_frame, text="Procurar...", command=self.browse_output_file)
        browse_button.pack(side=tk.LEFT)

        # --- Ação e Progresso ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(action_frame, text="Criar Imagem", command=self.start_imaging_thread)
        self.start_button.pack(side=tk.LEFT, padx=(0, 20))

        self.progress_bar = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Status ---
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.status_label = ttk.Label(status_frame, text="Pronto. Selecione o disco de origem e o arquivo de destino.", wraplength=550, justify=tk.LEFT)
        self.status_label.pack(anchor=tk.NW, padx=5, pady=5)

        # --- Inicialização ---
        self.refresh_disk_list()
        if not is_admin():
             self.status_label.config(text="AVISO: Execute como Administrador para poder criar a imagem!", foreground="red")
             messagebox.showwarning("Permissão Necessária", "Este programa precisa ser executado como Administrador para acessar os discos diretamente.\n\nFeche o programa, clique com o botão direito no arquivo (.py ou .exe) e selecione 'Executar como administrador'.")
             # Poderia desabilitar o botão aqui, mas o aviso é mais informativo
             # self.start_button.config(state=tk.DISABLED)


    def refresh_disk_list(self):
        """Busca a lista de discos e atualiza a Listbox."""
        self.status_label.config(text="Procurando discos...", foreground="black")
        self.root.update_idletasks() # Força atualização da GUI
        self.disks = list_disks_windows()
        self.disk_listbox.delete(0, tk.END) # Limpa a lista
        self.selected_disk_info = None
        self.start_button.config(state=tk.DISABLED) # Desabilita botão até selecionar

        if not self.disks:
            self.status_label.config(text="Nenhum disco encontrado ou erro ao listar.", foreground="red")
            self.disk_listbox.insert(tk.END, "Nenhum disco encontrado")
            self.disk_listbox.config(state=tk.DISABLED)
        else:
             self.disk_listbox.config(state=tk.NORMAL)
             for i, disk in enumerate(self.disks):
                 self.disk_listbox.insert(tk.END, disk["display_text"])
                 # Destacar discos que não parecem removíveis
                 if not disk["likely_removable"]:
                     self.disk_listbox.itemconfig(i, {'fg': 'orange'}) # Laranja para atenção
             self.status_label.config(text="Selecione o disco de origem na lista.", foreground="black")

    def on_disk_select(self, event):
        """Chamado quando um item na Listbox é selecionado."""
        selection = self.disk_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_disk_info = self.disks[index]
            # Pré-preenche o nome do arquivo de saída
            safe_filename = f"backup_disk{self.selected_disk_info['index']}.img"
            current_output = self.output_file_path.get()
            # Só preenche se estiver vazio ou for o nome padrão anterior
            if not current_output or current_output.startswith("backup_disk"):
                 self.output_file_path.set(os.path.join(os.getcwd(), safe_filename)) # Põe no diretório atual por padrão

            self.status_label.config(text=f"Disco selecionado: {self.selected_disk_info['display_text']}", foreground="blue")
            if self.output_file_path.get(): # Habilita botão se ambos estiverem selecionados
                 self.start_button.config(state=tk.NORMAL)
            else:
                 self.start_button.config(state=tk.DISABLED)

            # Aviso extra se não for removível
            if not self.selected_disk_info["likely_removable"]:
                 self.status_label.config(text=f"ATENÇÃO: '{self.selected_disk_info['model']}' não parece ser removível! Tenha CERTEZA!", foreground="red")

        else:
            self.selected_disk_info = None
            self.start_button.config(state=tk.DISABLED)
            self.status_label.config(text="Nenhum disco selecionado.", foreground="black")

    def browse_output_file(self):
        """Abre a janela para selecionar o local e nome do arquivo de saída."""
        # Sugere um nome de arquivo baseado no disco selecionado, se houver
        initial_filename = "disk_image.img"
        if self.selected_disk_info:
            initial_filename = f"backup_disk{self.selected_disk_info['index']}.img"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".img",
            filetypes=[("Arquivos de Imagem", "*.img"), ("Todos os Arquivos", "*.*")],
            initialfile=initial_filename,
            title="Salvar Imagem de Disco Como"
        )
        if file_path:
            self.output_file_path.set(file_path)
            if self.selected_disk_info: # Habilita botão se ambos estiverem ok
                 self.start_button.config(state=tk.NORMAL)


    def update_progress(self, value):
        """Callback para atualizar a barra de progresso (thread-safe)."""
        self.progress_bar['value'] = value
        # Forçar atualização da GUI (pode não ser estritamente necessário com ttk)
        # self.root.update_idletasks()

    def update_status(self, message, color="black"):
        """Callback para atualizar a label de status (thread-safe)."""
        self.status_label.config(text=message, foreground=color)
        # Forçar atualização da GUI
        # self.root.update_idletasks()

    def start_imaging_thread(self):
        """Inicia a criação da imagem em uma thread separada."""
        if not self.selected_disk_info:
            messagebox.showerror("Erro", "Nenhum disco de origem selecionado.")
            return
        if not self.output_file_path.get():
            messagebox.showerror("Erro", "Nenhum arquivo de imagem de saída selecionado.")
            return

        source_path = self.selected_disk_info['device_id']
        source_size = self.selected_disk_info['size_bytes']
        output_path = self.output_file_path.get()

        # Verificação de segurança crucial
        msg = (f"Você está prestes a criar uma imagem do disco:\n\n"
               f"Origem: {self.selected_disk_info['display_text']}\n"
               f"ID Físico: {source_path}\n\n"
               f"Destino: {output_path}\n\n"
               f"Isso lerá TODO o conteúdo do disco de origem ({self.selected_disk_info['size_formatted']}).\n"
               f"TEM CERTEZA ABSOLUTA QUE A ORIGEM ESTÁ CORRETA?")
        if not self.selected_disk_info['likely_removable']:
             msg += "\n\nATENÇÃO: O disco selecionado NÃO parece ser removível (Pendrive/SD). RISCO ALTO se selecionado incorretamente!"

        if messagebox.askyesno("Confirmação Final", msg, icon='warning'):
            # Verifica se o arquivo de saída já existe
            if os.path.exists(output_path):
                 if not messagebox.askyesno("Sobrescrever?", f"O arquivo '{os.path.basename(output_path)}' já existe. Deseja sobrescrevê-lo?", icon='warning'):
                      self.update_status("Operação cancelada pelo usuário (não sobrescrever).", "orange")
                      return

            # Desabilita controles e inicia a thread
            self.start_button.config(state=tk.DISABLED)
            self.disk_listbox.config(state=tk.DISABLED) # Impede seleção durante cópia
            # Limpa progresso anterior
            self.progress_bar['value'] = 0

            # Cria e inicia a thread worker
            self.worker_thread = threading.Thread(
                target=create_image_worker,
                args=(source_path, output_path, source_size,
                      # Passa métodos da instância que podem ser chamados pela thread
                      # Tkinter é geralmente thread-safe para chamadas de config/update via métodos
                      # mas é mais robusto usar root.after se houver problemas.
                      # Para simplificar, tentamos a chamada direta primeiro.
                      self.update_progress_safe,
                      self.update_status_safe),
                daemon=True # Permite que o programa feche mesmo se a thread estiver rodando
            )
            self.worker_thread.start()

            # Agenda verificação do status da thread (opcional, mas bom para reabilitar botões)
            self.root.after(100, self.check_worker_thread)

        else:
            self.update_status("Operação cancelada pelo usuário.", "orange")

    # Wrappers seguros para chamar a partir da thread usando root.after
    def update_progress_safe(self, value):
        self.root.after(0, self.update_progress, value)

    def update_status_safe(self, message, color="black"):
        self.root.after(0, self.update_status, message, color)

    def check_worker_thread(self):
        """Verifica se a thread worker terminou e reabilita os controles."""
        if self.worker_thread.is_alive():
            # Ainda rodando, verifica de novo depois
            self.root.after(100, self.check_worker_thread)
        else:
            # Terminou, reabilita
            self.start_button.config(state=tk.NORMAL if self.selected_disk_info and self.output_file_path.get() else tk.DISABLED)
            self.disk_listbox.config(state=tk.NORMAL)
            # Atualiza a lista caso um disco tenha sido removido/adicionado
            # self.refresh_disk_list() # Opcional: pode ser confuso atualizar automaticamente


# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    # Verifica Admin ANTES de criar a janela principal
    if not is_admin():
         # Tenta re-executar como admin
         try:
              ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
              sys.exit(0) # Sai do processo não-admin
         except Exception as e:
              root = tk.Tk()
              root.withdraw() # Esconde a janela principal vazia
              messagebox.showerror("Erro de Permissão", f"Falha ao tentar elevar privilégios: {e}\n\nPor favor, execute o programa como Administrador.")
              sys.exit(1)

    # Se chegou aqui, ou já é admin, ou a re-execução foi iniciada
    # No caso da re-execução, o processo original saiu, e o novo (admin) continua aqui.
    root = tk.Tk()
    app = DiskImagerApp(root)
    root.mainloop()