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

        self.pairs_label = ttk.Label(master, text="Paires de Crypto (séparées par des virgules):")
        self.pairs_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.pairs_entry = ttk.Entry(master)
        self.pairs_entry.grid(row=0, column=1, padx=10, pady=10)

        self.check_button = ttk.Button(master, text="Vérifier les Prix", command=self.check_prices)
        self.check_button.grid(row=0, column=2, padx=10, pady=10)

        self.price_label = ttk.Label(master, text="Prix en Temps Réel (USD):")
        self.price_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.price_display = ttk.Label(master, text="")
        self.price_display.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky='w')

        # Nouveaux labels pour afficher les derniers prix d'achat et de vente
        self.last_buy_label = ttk.Label(master, text="Dernier Achat (USD):")
        self.last_buy_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.last_sell_label = ttk.Label(master, text="Dernière Vente (USD):")
        self.last_sell_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

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
        # Définir la fonction de mise à jour des prix à intervalles réguliers (en commentant cette ligne)
        # self.update_prices()

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

            # Mettre à jour les derniers prix d'achat et de vente avec des valeurs fictives pour l'instant
            self.update_last_prices()

            # Sauvegarder les préférences après chaque vérification des prix
            self.save_preferences()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {str(e)}")

    # Fonction de mise à jour manuelle des prix
    def update_prices(self):
        # Mettre à jour les prix
        pairs = [pair.strip().lower() for pair in self.pairs_entry.get().split(",")]

        try:
            prices = self.get_crypto_prices(pairs)
            formatted_prices = "\n".join([f"{pair}: {price['usd']} USD" for pair, price in prices.items()])
            self.price_display.config(text=f"Prix actuels :\n{formatted_prices}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {str(e)}")

    def update_last_prices(self):
        # Mettre à jour les derniers prix d'achat et de vente avec les valeurs enregistrées
        try:
            last_buy_price = float(self.config.get('Preferences', 'LastBuyPrice'))
            last_sell_price = float(self.config.get('Preferences', 'LastSellPrice'))

            # Afficher les derniers prix dans les labels correspondants
            self.last_buy_label.config(text=f"Dernier Achat (USD): {last_buy_price:.2f} USD")
            self.last_sell_label.config(text=f"Dernière Vente (USD): {last_sell_price:.2f} USD")
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(f"Erreur lors de la mise à jour des derniers prix : {e}")
            # Vous pouvez ajouter un message d'erreur supplémentaire si nécessaire


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

        if last_type.lower() == "achat":
            self.last_buy_label.config(text=f"Dernier Achat (USD): {last_price} USD")
        elif last_type.lower() == "vente":
            self.last_sell_label.config(text=f"Dernière Vente (USD): {last_price} USD")
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner un type valide (Achat/Vente).")
            return

        # Sauvegarder les préférences après chaque enregistrement du dernier prix
        self.save_preferences()








    def edit_last_price(self):
        # Modifier le dernier prix en ouvrant une nouvelle fenêtre de modification
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Modifier le Dernier Prix")

        # Champs d'entrée pour modifier le dernier prix et le type (achat/vente)
        edit_price_label = ttk.Label(edit_window, text="Nouveau Prix:")
        edit_price_label.grid(row=0, column=0, padx=10, pady=10)

        edit_price_entry = ttk.Entry(edit_window)
        edit_price_entry.grid(row=0, column=1, padx=10, pady=10)

        edit_type_label = ttk.Label(edit_window, text="Nouveau Type:")
        edit_type_label.grid(row=1, column=0, padx=10, pady=10)

        edit_type_entry = ttk.Combobox(edit_window, values=["Achat", "Vente"])
        edit_type_entry.grid(row=1, column=1, padx=10, pady=10)

        # Bouton pour appliquer la modification
        apply_button = ttk.Button(edit_window, text="Appliquer", command=lambda: self.apply_edit(edit_window, edit_price_entry, edit_type_entry))
        apply_button.grid(row=2, column=0, columnspan=2, pady=10)

    def apply_edit(self, edit_window, edit_price_entry, edit_type_entry):
        # Appliquer la modification du dernier prix
        new_price = edit_price_entry.get()
        new_type = edit_type_entry.get()

        # Vous devriez également vérifier si new_price est un nombre valide
        try:
            new_price = float(new_price)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir un nombre valide pour le prix.")
            return

        if new_type.lower() == "achat":
            self.last_buy_label.config(text=f"Dernier Achat (USD): {new_price} USD")
        elif new_type.lower() == "vente":
            self.last_sell_label.config(text=f"Dernière Vente (USD): {new_price} USD")
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner un type valide (Achat/Vente).")
            return

        # Sauvegarder les préférences après chaque modification du dernier prix
        self.save_preferences()

        # Fermer la fenêtre de modification
        edit_window.destroy()

    def save_last_prices(self):
        # Sauvegarder les derniers prix dans le fichier de préférences
        last_buy_price = self.last_buy_label.cget("text").split(":")[1].strip()
        last_sell_price = self.last_sell_label.cget("text").split(":")[1].strip()

        self.config.set('Preferences', 'LastBuyPrice', last_buy_price)
        self.config.set('Preferences', 'LastSellPrice', last_sell_price)

        with open('preferences.ini', 'w') as configfile:
            self.config.write(configfile)

    def load_last_prices(self):
        # Charger les derniers prix depuis le fichier de préférences
        try:
            last_buy_price = self.config.get('Preferences', 'LastBuyPrice')
            last_sell_price = self.config.get('Preferences', 'LastSellPrice')

            self.last_buy_label.config(text=f"Dernier Achat (USD): {last_buy_price} USD")
            self.last_sell_label.config(text=f"Dernière Vente (USD): {last_sell_price}")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            print(f"Erreur lors du chargement des derniers prix : {e}")

    def save_preferences(self):
        # Sauvegarder les préférences dans un fichier
        pairs_value = self.pairs_entry.get()
        print(f"Saving preferences: Pairs={pairs_value}")
        self.config.set('Preferences', 'Pairs', pairs_value)
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
        except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError) as e:
            print(f"Erreur lors du chargement des préférences : {e}")

    def save_and_quit(self):
        # Sauvegarder les préférences avant de quitter l'application
        self.save_preferences()
        self.save_last_prices()
        self.master.quit()

def main():
    root = tk.Tk()
    app = CryptoPriceTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
