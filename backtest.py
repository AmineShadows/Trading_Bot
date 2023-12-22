import tkinter as tk
from tkinter import ttk, messagebox
import requests
import configparser

class CryptoPriceTracker:
    def __init__(self, master):
        self.master = master
        master.title("Crypto Price Tracker")

        # Initialiser le gestionnaire de configuration
        self.config = configparser.ConfigParser()

        # Créer la section 'Preferences' si elle n'existe pas
        if 'Preferences' not in self.config:
            self.config.add_section('Preferences')

        # Créer la section 'Prices' si elle n'existe pas
        if 'Prices' not in self.config:
            self.config.add_section('Prices')

        # Créer un Treeview pour afficher le tableau
        self.tree = ttk.Treeview(master, columns=("Paire", "Dernier Achat", "Dernière Vente"))
        self.tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.tree.heading("#0", text="Paires")
        self.tree.heading("#1", text="Dernier Achat")
        self.tree.heading("#2", text="Dernière Vente")

        self.pairs_label = ttk.Label(master, text="Paires de Crypto (séparées par des virgules):")
        self.pairs_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.pairs_entry = ttk.Entry(master)
        self.pairs_entry.grid(row=2, column=1, padx=10, pady=10)

        self.check_button = ttk.Button(master, text="Vérifier les Prix", command=self.check_prices)
        self.check_button.grid(row=2, column=2, padx=10, pady=10)

        self.price_label = ttk.Label(master, text="Prix en Temps Réel (USD):")
        self.price_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.price_display = ttk.Label(master, text="")
        self.price_display.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky='w')

        # Champs d'entrée pour saisir le dernier prix et le type (achat/vente)
        self.last_price_entry = ttk.Entry(master)
        self.last_type_entry = ttk.Combobox(master, values=["Achat", "Vente"])
        self.last_type_entry.set("Achat")

        self.last_price_entry.grid(row=4, column=1, padx=10, pady=10)
        self.last_type_entry.grid(row=4, column=2, padx=10, pady=10)

        # Boutons pour valider et modifier les derniers prix
        self.save_button = ttk.Button(master, text="Enregistrer Prix", command=self.save_last_price)
        self.save_button.grid(row=5, column=1, padx=10, pady=10)

        self.edit_button = ttk.Button(master, text="Modifier Prix", command=self.edit_last_price)
        self.edit_button.grid(row=5, column=2, padx=10, pady=10)

        self.quit_button = ttk.Button(master, text="Quitter", command=self.save_and_quit)
        self.quit_button.grid(row=6, column=0, columnspan=3, pady=10)

        # Charger les préférences sauvegardées
        self.load_preferences()
        self.load_last_prices() 

    def get_crypto_prices(self, symbols):
        try:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={",".join(symbols)}&vs_currencies=usd'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.HTTPError as errh:
            raise Exception(f"Erreur HTTP : {errh}")
        except requests.exceptions.ConnectionError as errc:
            raise Exception(f"Erreur de connexion : {errc}")
        except requests.exceptions.Timeout as errt:
            raise Exception(f"Timeout : {errt}")
        except requests.exceptions.RequestException as err:
            raise Exception(f"Erreur lors de la requête : {err}")

    def check_prices(self):
        pairs = [pair.strip().lower() for pair in self.pairs_entry.get().split(",")]

        try:
            prices = self.get_crypto_prices(pairs)
            formatted_prices = "\n".join([f"{pair}: {price['usd']} USD" for pair, price in prices.items()])
            self.price_display.config(text=f"Prix actuels :\n{formatted_prices}")

            # Ajouter la paire et les derniers prix au tableau
            for pair in pairs:
                self.add_pair_to_table(pair, "", "")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {str(e)}")

    def add_pair_to_table(self, pair, last_buy, last_sell):
        self.tree.insert("", "end", values=(pair, last_buy, last_sell))

    def save_last_price(self):
        # Enregistrer le dernier prix avec le type (achat/vente) dans les préférences
        last_price_str = self.last_price_entry.get()
        last_type = self.last_type_entry.get()

        # Remplacer les virgules par des points dans le prix
        last_price_str = last_price_str.replace(",", ".")

        # Vérifier s'il y a plus d'une virgule ou d'un point
        if last_price_str.count('.') > 1 or last_price_str.count(',') > 1:
            messagebox.showerror("Erreur", "Veuillez saisir un nombre valide pour le prix.")
            return

        # Vous devriez également vérifier si last_price est un nombre valide
        try:
            last_price = float(last_price_str)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir un nombre valide pour le prix.")
            return

        selected_item = self.tree.selection()

        if selected_item:
            # Mettre à jour la ligne sélectionnée avec les nouveaux prix
            self.tree.item(selected_item, values=(selected_item[0], last_price, last_type))
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner une paire dans le tableau.")
            return

        # Sauvegarder les préférences après chaque enregistrement du dernier prix
        self.save_preferences()

    def edit_last_price(self):
        # Modifier le dernier prix en ouvrant une nouvelle fenêtre de modification
        selected_item = self.tree.selection()

        if selected_item:
            # Extraire les valeurs de la ligne sélectionnée
            pair, last_buy, last_sell = self.tree.item(selected_item, 'values')

            # Remplir les champs d'entrée avec les valeurs existantes
            self.last_price_entry.delete(0, tk.END)
            self.last_price_entry.insert(0, last_buy)
            self.last_type_entry.set(last_sell)

            # Appeler la méthode pour sauvegarder le dernier prix après modification
            self.save_last_price()
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner une paire dans le tableau.")

    def save_preferences(self):
        # Sauvegarder les préférences dans un fichier
        pairs_value = self.pairs_entry.get()
        print(f"Saving preferences: Pairs={pairs_value}")
        self.config.set('Preferences', 'Pairs', pairs_value)

        # Sauvegarder les paires dans la section 'Prices'
        self.config.remove_section('Prices')
        self.config.add_section('Prices')
        for item in self.tree.get_children():
            pair, last_buy, last_sell = self.tree.item(item, 'values')
            self.config.set('Prices', pair, f"{last_buy},{last_sell}")

        with open('preferences.ini', 'w') as configfile:
            self.config.write(configfile)

    def load_preferences(self):
        # Charger les préférences depuis le fichier
        try:
            self.config.read('preferences.ini')

            # Vérifier si la section 'Preferences' existe avant de récupérer les paires
            if 'Preferences' in self.config:
                pairs = self.config.get('Preferences', 'Pairs')
                print(f"Loading preferences: Pairs={pairs}")
                self.pairs_entry.insert(0, pairs)

            # Charger les paires depuis la section 'Prices'
            if 'Prices' in self.config:
                for pair, prices in self.config.items('Prices'):
                    last_buy, last_sell = prices.split(',')
                    self.add_pair_to_table(pair, last_buy, last_sell)

        except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError) as e:
            print(f"Erreur lors du chargement des préférences : {e}")

    def load_last_prices(self):
        # Charger les derniers prix depuis le fichier de préférences
        pass  # Pas besoin de charger les derniers prix ici

    def save_and_quit(self):
        # Sauvegarder les préférences avant de quitter l'application
        self.save_preferences()
        self.master.quit()

def main():
    root = tk.Tk()
    app = CryptoPriceTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
