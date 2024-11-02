# Vérification de pip
if ! command -v pip &> /dev/null; then
    echo "Erreur : pip n'est pas installé. Installez pip avant de continuer."
    exit 1
fi

# Vérification de Python 3.12
if ! command -v python3 &> /dev/null; then
    echo "Erreur : Python n'est pas installé. Installez Python 3.12 avant de continuer."
    exit 1
else
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    if [[ "$python_version" != 3.12* ]]; then
        echo "Erreur : Python 3.12 est requis. Version trouvée : $python_version"
        exit 1
    fi
fi

# Vérification de npm
if ! command -v npm &> /dev/null; then
    echo "Erreur : npm n'est pas installé. Installez npm avant de continuer."
    exit 1
fi


cd backend
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
echo "Pour lancer le backend vous pouvez exécuter ``uvicorn main:app --host 0.0.0.0 --port 8000 --reload``"

cd ../frontend
npm install
echo "Pour lancer le frontend vous pouvez exécuter ``npm run dev``"

cd ..