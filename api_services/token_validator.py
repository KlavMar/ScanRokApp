class TokenValidator:
    pass 

# gatekeeper.py
import sys, requests
from cores.storage import StorageSqlite
from PyQt6.QtWidgets import QApplication, QInputDialog, QMessageBox
import uuid
VERIFY_URL = "http://localhost:8000/billing/verify-access/"  # GET → 200 {"ok": true} attendu

def prompt_token() -> str | None:
    app = QApplication.instance() or QApplication(sys.argv)
    token, ok = QInputDialog.getText(None, "Connexion requise",
                                     "Collez votre token d’abonnement :")
    return token.strip() if ok and token else None

def verify_online(token: str) -> bool:
    try:
        machine_id = uuid.getnode()
        r = requests.get(VERIFY_URL, headers={"Authorization": f"Bearer {token}","X-Device-Id": str(machine_id)}, timeout=8)
        if r.status_code == 200:
            return r.json()
        
    except Exception as e:
        print(e)
        return False

def gatekeeper_or_exit() -> str:
    app = QApplication.instance() or QApplication(sys.argv)
    bdd = StorageSqlite()
    token = bdd.load()
    r =   verify_online(token)
    if token and r.get("ok") == True:
        return token

    token = prompt_token()
    if not token or not verify_online(token).get("ok"):
        QMessageBox.critical(None, "Access Forbidden, please renew Token or contact Support")
        sys.exit(1)

    r = verify_online(token)
    r.update({"token":token})
    bdd.save(r)
    return token
