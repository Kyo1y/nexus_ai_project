# Install Guide

## Setting up Front-End React App
### Step 1: Install **nvm**
First, make sure that `nvm` is installed. Use `curl` to install
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```
### Step 2: Install **node**
```bash
nvm install 16
```
### Step 3: Install **yarn**
```bash
npm install --global yarn
```
### Step 4: Install local packages
```bash
cd fp-react
yarn install
```

### Step 5: Run app
```bash
yarn start
```

## Setting up Python
### Step 1: Create Conda 
```bash
conda create -n fp-assist Python=3.8.16
```
### Step 2: Activate and install requirements
```bash
conda activate fp-assist
pip install -r requirements.txt
```