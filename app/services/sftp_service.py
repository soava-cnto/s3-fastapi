import paramiko
import re
from io import BytesIO
from datetime import datetime
from typing import Optional, List
from app.core.config import settings


class SFTPService:
    """Service pour gérer les connexions SFTP et lire les fichiers"""
    
    def __init__(self):
        self.ssh_client = None
        self.sftp_client = None
    
    def connect(self):
        """Établit une connexion SFTP"""
        if not all([settings.SFTP_HOST, settings.SFTP_USERNAME, settings.SFTP_PASSWORD]):
            raise ValueError("Configuration SFTP incomplète: host, username et password requis")
        
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh_client.connect(
                hostname=settings.SFTP_HOST,
                port=settings.SFTP_PORT,
                username=settings.SFTP_USERNAME,
                password=settings.SFTP_PASSWORD
            )
            
            self.sftp_client = self.ssh_client.open_sftp()
        except Exception as e:
            raise Exception(f"Erreur de connexion SFTP: {str(e)}")
    
    def disconnect(self):
        """Ferme la connexion SFTP"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
            if self.ssh_client:
                self.ssh_client.close()
        except Exception as e:
            print(f"Erreur lors de la fermeture SFTP: {str(e)}")
    
    def list_files(self, remote_path: str) -> List[str]:
        """Liste les fichiers dans le répertoire distant"""
        try:
            if not self.sftp_client:
                self.connect()
            
            files = self.sftp_client.listdir(remote_path)
            return files
        except Exception as e:
            raise Exception(f"Erreur lors de la listage des fichiers: {str(e)}")
    
    def find_latest_activity_file(self) -> Optional[str]:
        """
        Trouve le dernier fichier d'activité au format:
        YYYY-MM-DD_S3_Activity_Historique_M(0)_to_J-1.csv
        """
        try:
            if not self.sftp_client:
                self.connect()
            
            remote_path = settings.SFTP_REMOTE_PATH
            files = self.list_files(remote_path)
            
            # Pattern regex pour les fichiers d'activité
            pattern = r'(\d{4}-\d{2}-\d{2})_S3_Activity_Historique_M\(0\)_to_J-1\.csv'
            
            matching_files = []
            for file in files:
                if re.match(pattern, file):
                    # Extraire la date du filename
                    match = re.match(pattern, file)
                    if match:
                        date_str = match.group(1)
                        try:
                            file_date = datetime.strptime(date_str, "%Y-%m-%d")
                            matching_files.append((file_date, file))
                        except ValueError:
                            continue
            
            if not matching_files:
                return None
            
            # Retourner le fichier avec la date la plus récente
            latest = max(matching_files, key=lambda x: x[0])
            return latest[1]
        
        except Exception as e:
            raise Exception(f"Erreur lors de la recherche du fichier: {str(e)}")
    
    def find_latest_activity_file_monthly(self) -> Optional[str]:
        """
        Trouve le dernier fichier d'activité monthly au format:
        S3_Activity_Historique_Monthly_YYYY-MM-DD.csv
        """
        try:
            if not self.sftp_client:
                self.connect()
            
            remote_path = settings.SFTP_REMOTE_PATH_MONTHLY or settings.SFTP_REMOTE_PATH
            files = self.list_files(remote_path)
            
            # Pattern regex pour les fichiers d'activité monthly
            pattern = r'S3_Activity_Historique_Monthly_(\d{4}-\d{2}-\d{2})\.csv'
            
            matching_files = []
            for file in files:
                if re.search(pattern, file):
                    # Extraire la date du filename
                    match = re.search(pattern, file)
                    if match:
                        date_str = match.group(1)
                        try:
                            file_date = datetime.strptime(date_str, "%Y-%m-%d")
                            matching_files.append((file_date, file))
                        except ValueError:
                            continue
            
            if not matching_files:
                return None
            
            # Retourner le fichier avec la date la plus récente
            latest = max(matching_files, key=lambda x: x[0])
            return latest[1]
        
        except Exception as e:
            raise Exception(f"Erreur lors de la recherche du fichier monthly: {str(e)}")
    
    def read_file_content(self, remote_file: str) -> bytes:
        """
        Lit le contenu d'un fichier distant et le retourne sous forme de bytes
        """
        try:
            if not self.sftp_client:
                self.connect()
            
            remote_path = f"{settings.SFTP_REMOTE_PATH.rstrip('/')}/{remote_file}"
            
            # Lire le fichier dans BytesIO
            file_obj = BytesIO()
            self.sftp_client.getfo(remote_path, file_obj)
            file_obj.seek(0)
            
            return file_obj.read()
        
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier {remote_file}: {str(e)}")
    
    def read_latest_activity_file(self) -> tuple[Optional[str], Optional[bytes]]:
        """
        Trouve et lit le dernier fichier d'activité (history)
        Retourne un tuple (nom_du_fichier, contenu)
        """
        try:
            filename = self.find_latest_activity_file()
            if not filename:
                return None, None
            
            content = self.read_file_content(filename)
            return filename, content
        
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du dernier fichier: {str(e)}")
        
        finally:
            self.disconnect()
    
    def read_latest_activity_file_monthly(self) -> tuple[Optional[str], Optional[bytes]]:
        """
        Trouve et lit le dernier fichier d'activité monthly
        Retourne un tuple (nom_du_fichier, contenu)
        """
        try:
            filename = self.find_latest_activity_file_monthly()
            if not filename:
                return None, None
            
            # Utiliser le chemin monthly pour lire le fichier
            remote_path = settings.SFTP_REMOTE_PATH_MONTHLY or settings.SFTP_REMOTE_PATH
            
            try:
                if not self.sftp_client:
                    self.connect()
                
                remote_file_path = f"{remote_path.rstrip('/')}/{filename}"
                
                # Lire le fichier dans BytesIO
                file_obj = BytesIO()
                self.sftp_client.getfo(remote_file_path, file_obj)
                file_obj.seek(0)
                
                content = file_obj.read()
                return filename, content
            except Exception as e:
                raise Exception(f"Erreur lors de la lecture du fichier {filename}: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du dernier fichier monthly: {str(e)}")
        
        finally:
            self.disconnect()
