"""
#######################################################
##### Application Hockey Prono -- Main Python File ####
#######################################################
"""


"""
###############################################
####### Importation des bibliothèques #########
###############################################
"""

# ----- Bibliothèques générales ----
# ----------------------------------
import json
import sqlite3
import string
import random
import uuid
import io
import pandas as pd
import requests
from datetime import datetime, timedelta
import psutil
import bcrypt
from cryptography.fernet import Fernet
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from io import StringIO
import csv
from psycopg2.extras import RealDictCursor
import webbrowser
from notifypy import Notify

# ----- Bibliothèques kivy ----
# ----------------------------------

import asynckivy
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.core.clipboard import Clipboard

#----- Bibliothèques KivyMD ------
#---------------------------------

from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton, MDTopAppBarTitle, \
    MDTopAppBarTrailingButtonContainer, MDTopAppBar
from kivymd.uix.behaviors import RotateBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.divider import MDDivider
from kivymd.uix.expansionpanel import MDExpansionPanel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import BaseDropdownItem
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon, MDNavigationItemLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.list import  MDListItemTrailingIcon
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.navigationrail import MDNavigationRailItem, MDNavigationRailItemIcon, MDNavigationRailItemLabel
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from kivymd.uix.tab import MDTabsItem, MDTabsItemIcon, MDTabsItemText
from kivymd.uix.responsivelayout import MDResponsiveLayout

from jnius import autoclass

# PythonActivity = autoclass('org.kivy.android.PythonActivity')
# Context = autoclass('android.content.Context')
# WorkManager = autoclass('androidx.work.WorkManager')
# OneTimeWorkRequest = autoclass('androidx.work.OneTimeWorkRequest')
# PeriodicWorkRequest = autoclass('androidx.work.PeriodicWorkRequest')
# WorkRequest = autoclass('androidx.work.WorkRequest')
# Data = autoclass('androidx.work.Data')
# TimeUnit = autoclass('java.util.concurrent.TimeUnit')

# app.create_notification_channel()
# show_notification("KivyMD Notification", "This is a test notification")


# ------------------------
# ---- Fonctions genérales
# ------------------------

def memory_usage():
    process = psutil.Process()
    usage = process.memory_info().rss
    return usage  # Returning the memory in bytes

"""
#-----------------------------------------------
#--- Hachage des mdp - secret.key, password.enc
#-----------------------------------------------
"""
import os
import re
from cryptography.fernet import Fernet
import bcrypt
import base64


class SecureStorage:
    def __init__(self, key_file='secret.key'):
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, 'wb') as key_file:
                key_file.write(key)
        else:
            with open(key_file, 'rb') as key_file:
                key = key_file.read()

        self.fernet = Fernet(key)
        self.password_file = 'passwords.enc'

    def validate_password(self, password):
        print(f"Validating password: {password}")
        if len(password) > 10:
            raise ValueError("Password must be 10 characters or less")

        forbidden_chars = r'[\x00-\x1F\\:;"\'`&|<>]'
        match = re.search(forbidden_chars, password)
        if match:
            raise ValueError(f"Password contains forbidden character: {match.group()}")
        print("Password validation successful")
        return True

    def store_password(self, email, hashed_password):
        print(f"Storing password for email: {email}")
        print(f"Hashed Password: {hashed_password}")
        encoded_data = base64.b64encode(f"{email}:{hashed_password}".encode()).decode()
        encrypted_data = self.fernet.encrypt(encoded_data.encode())
        print(f"Encrypted data length: {len(encrypted_data)}")

        existing_passwords = []
        if os.path.exists(self.password_file):
            with open(self.password_file, 'rb') as file:
                existing_passwords = file.readlines()

        updated = False
        with open(self.password_file, 'wb') as file:
            for line in existing_passwords:
                decrypted_data = self.fernet.decrypt(line.strip()).decode()
                decoded_data = base64.b64decode(decrypted_data).decode()
                stored_email, _ = decoded_data.split(':')
                if stored_email == email:
                    file.write(encrypted_data + b'\n')
                    updated = True
                else:
                    file.write(line)

            if not updated:
                file.write(encrypted_data + b'\n')

    def get_password(self, email):
        if not os.path.exists(self.password_file):
            print("Password file not found")
            return None

        with open(self.password_file, 'rb') as file:
            lines = file.readlines()
            for line in reversed(lines):
                try:
                    decrypted_data = self.fernet.decrypt(line.strip()).decode()
                    decoded_data = base64.b64decode(decrypted_data).decode()
                    stored_email, stored_password = decoded_data.split(':', 1)
                    if stored_email == email:
                        print(f"Password found for email: {email}")
                        return stored_password
                except Exception as e:
                    print(f"Error processing line: {e}")
        print(f"Password not found for email: {email}")
        return None

    @staticmethod
    def hash_password(password):
        print(f"Hashing password: {password}")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Hashed result: {hashed}")
        return hashed

    def verify_password(self, stored_password, provided_password):
        print(f"Verifying password")
        print(f"Stored password: {stored_password}")
        print(f"Provided password: {provided_password}")
        result = bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
        print(f"Verification result: {result}")
        return result

"""
#################################
#### Déclaration des classes ####
#################################
"""

#-------- TopAppBar ---------------
#--------------------------------
class MDTopAppBar(MDTopAppBar):
    pass

class MDTopAppBarLeadingButtonContainer(MDTopAppBarLeadingButtonContainer):
    pass

class MDActionTopAppBarButton(MDActionTopAppBarButton):
    pass

class MDTopAppBarTitle(MDTopAppBarTitle):
    pass

class MDTopAppBarTrailingButtonContainer(MDTopAppBarTrailingButtonContainer):
    pass

#-------- Navigation Bar---------
#--------------------------------

class MDNavigationBar(MDNavigationBar):
    pass

class MDNavigationItem(MDNavigationItem):
    pass

class MDNavigationItemIcon(MDNavigationItemIcon):
    pass

class MDNavigationItemLabel(MDNavigationItemLabel):
    pass

class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()

#-------- Layouts ---------------
#--------------------------------

class MDBoxLayout(MDBoxLayout):
    pass

class BoxLayout(BoxLayout):
    pass

class MDScrollView(MDScrollView):
    pass

#-------- Boutons ---------------
#--------------------------------

class MDButton(MDButton):
    pass

class MDButtonText(MDButtonText):
    pass

#-------- Opérateurs---------------
#--------------------------------

class MDDivider(MDDivider):
    pass

class MDRefreshLayout(MDScrollViewRefreshLayout):
    pass

#-------- Menu ---------------
#--------------------------------

class MDDropdownMenu(MDDropdownMenu):
    pass

class BaseDropDownItem(BaseDropdownItem):
    pass

#-------- Screens ---------------
#--------------------------------

class MDScreenManager(MDScreenManager):
    pass

class BaseScreenLM_Classement(MDScreen):
    image_size = StringProperty()
    rank_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.rank_text = app.get_translation("Rank")

class BaseScreenLM_Pronostics(MDScreen):
    image_size = StringProperty()

class BaseScreenLM_Rankings(MDScreen):
    image_size = StringProperty()
    rank_text = StringProperty()
    team_text = StringProperty()
    gp_text = StringProperty()
    w_text = StringProperty()
    otw_text = StringProperty()
    otl_text = StringProperty()
    l_text = StringProperty()
    gf_text = StringProperty()
    ga_text = StringProperty()
    pim_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.rank_text = app.get_translation("Rank")
        self.team_text = app.get_translation("Team")
        self.gp_text = app.get_translation("GP")
        self.w_text = app.get_translation("W")
        self.otw_text = app.get_translation("OTW")
        self.otl_text = app.get_translation("OTL")
        self.l_text = app.get_translation("L")
        self.gf_text = app.get_translation("GF")
        self.ga_text = app.get_translation("GA")
        self.pim_text = app.get_translation("PIM")

## NL ##
class BaseScreenNL_Classement(MDScreen):
    image_size = StringProperty()
    rank_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.rank_text = app.get_translation("Rank")

class BaseScreenNL_Pronostics(MDScreen):
    image_size = StringProperty()

class BaseScreenNL_Rankings(MDScreen):
    image_size = StringProperty()
    rank_text = StringProperty()
    team_text = StringProperty()
    gp_text = StringProperty()
    w_text = StringProperty()
    otw_text = StringProperty()
    otl_text = StringProperty()
    l_text = StringProperty()
    gf_text = StringProperty()
    ga_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.rank_text = app.get_translation("Rank")
        self.team_text = app.get_translation("Team")
        self.gp_text = app.get_translation("GP")
        self.w_text = app.get_translation("W")
        self.otw_text = app.get_translation("OTW")
        self.otl_text = app.get_translation("OTL")
        self.l_text = app.get_translation("L")
        self.gf_text = app.get_translation("GF")
        self.ga_text = app.get_translation("GA")

## FourNations ##
class BaseScreenFourNations_Classement(MDScreen):
    image_size = StringProperty()
    rank_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.rank_text = app.get_translation("Rank")

class BaseScreenFourNations_Pronostics(MDScreen):
    image_size = StringProperty()

class BaseScreenFourNations_Rankings(MDScreen):
    image_size = StringProperty()
    rank_text = StringProperty()
    team_text = StringProperty()
    gp_text = StringProperty()
    w_text = StringProperty()
    otw_text = StringProperty()
    otl_text = StringProperty()
    l_text = StringProperty()
    gf_text = StringProperty()
    ga_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.rank_text = app.get_translation("Rank")
        self.team_text = app.get_translation("Team")
        self.gp_text = app.get_translation("GP")
        self.w_text = app.get_translation("W")
        self.otw_text = app.get_translation("OTW")
        self.otl_text = app.get_translation("OTL")
        self.l_text = app.get_translation("L")
        self.gf_text = app.get_translation("GF")
        self.ga_text = app.get_translation("GA")

# Classe permettant à l'ExpansionPanel de s'étendre
# ---------------------------------------
class TrailingPressedIconButton(ButtonBehavior, RotateBehavior, MDListItemTrailingIcon):
    pass

# Classes d'ExpansionPanel
# -----------------------
class ExpansionPanelItemConnection(MDExpansionPanel):
    log_in_text = StringProperty()
    enter_your_informations_text = StringProperty()
    enter_email_text = StringProperty()
    email_text = StringProperty()
    password_text = StringProperty()
    forgot_password_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.log_in_text = app.get_translation("Log In")
        self.enter_your_informations_text = app.get_translation("Enter your informations")
        self.enter_email_text = app.get_translation("Enter email")
        self.email_text = app.get_translation("Email")
        self.password_text = app.get_translation("Password")
        self.forgot_password_text = app.get_translation("Forgot your password ?")

class ExpansionPanelItemInscription(MDExpansionPanel):
    register_text = StringProperty()
    enter_your_informations_text = StringProperty()
    enter_email_text = StringProperty()
    email_text = StringProperty()
    password_text = StringProperty()
    confirm_password_text = StringProperty()
    avoid_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.register_text = app.get_translation("Register")
        self.enter_your_informations_text = app.get_translation("Enter your informations")
        self.enter_email_text = app.get_translation("Enter email")
        self.email_text = app.get_translation("Email")
        self.password_text = app.get_translation("Password")
        self.confirm_password_text = app.get_translation("Confirm a password")
        self.avoid_text = app.get_translation("Avoid")

class ExpansionPanelItemVerification(MDExpansionPanel):
    verify_text= StringProperty()
    verify_email_adress_text =  StringProperty()
    enter_email_text = StringProperty()
    email_registered_text = StringProperty()
    code_received_text = StringProperty()
    six_digit_code_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.verify_text = app.get_translation("Verify")
        self.verify_email_adress_text = app.get_translation("Verify your email adress")
        self.enter_email_text = app.get_translation("Enter Email")
        self.email_registered_text = app.get_translation("Email registered")
        self.code_received_text = app.get_translation("Code received")
        self.six_digit_code_text = app.get_translation("Six digit code")

    def verify_code(self):
        app = MDApp.get_running_app()
        email = self.ids.verify_email.text
        entered_code = self.ids.verification_code.text

        if not email or not entered_code:
            app.show_snackbar(app.get_translation("Please fill in all fields"))
            return

        app.verify_email_code(email, entered_code)

"""
######################################
####### Ruban déroulant Icon  ########
######################################
"""

class IconSelectionPanel(MDExpansionPanel):
    selected_icon = StringProperty("account-circle-outline")
    select_icon_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.select_icon_text = app.get_translation("Select Icon")

    def select_icon(self, icon):
        self.selected_icon = icon
        self.ids.selected_icon.icon = icon

        app = MDApp.get_running_app()
        if app.current_user:
            try:
                with app.db_connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET icon = %s WHERE email = %s",
                        (icon, app.current_user['email'])
                    )
                    app.db_connection.commit()
                app.current_user['icon'] = icon
            except Exception as e:
                print(f"Error updating icon: {e}")
                app.show_snackbar(app.get_translation("Error updating icon. Please try again."))

        if hasattr(self.parent.parent, 'on_icon_select'):
            self.parent.parent.on_icon_select(icon)

"""
######################################
####### Ecran de registration ########
######################################
"""

class SetupProfileScreen(MDScreen):
    selected_icon = StringProperty("account-circle-outline")
    enter_your_pseudo_text = StringProperty()
    set_up_your_profile_text = StringProperty()
    save_and_continue_text= StringProperty()
    change_theme_text = StringProperty()
    languages_text = StringProperty()
    deconnect_text = StringProperty()
    contact_support_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.enter_your_pseudo_text = app.get_translation("Enter your pseudo")
        self.set_up_your_profile_text = app.get_translation("Set Up Your Profile")
        self.save_and_continue_text = app.get_translation("Save and Continue")
        self.change_theme_text = app.get_translation("Change Theme")
        self.languages_text = app.get_translation("Languages")
        self.deconnect_text = app.get_translation("Deconnect")
        self.contact_support_text = app.get_translation("Contact Support")

    def on_icon_select(self, icon):
        self.selected_icon = icon

    def save_profile(self):
        app = MDApp.get_running_app()
        pseudo = self.ids.pseudo_field.text
        if not pseudo:
            MDSnackbar(MDSnackbarText(text=app.get_translation("Please enter a pseudo"))).open()
            return

        app = MDApp.get_running_app()
        if app.current_user is None:
            MDSnackbar(MDSnackbarText(text=app.get_translation("Error: User not registered"))).open()
            return

        selected_icon = self.ids.icon_selection.selected_icon

        try:
            with app.db_connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET pseudo = %s, icon = %s WHERE email = %s",
                    (pseudo, selected_icon, app.current_user['email'])
                )
                app.db_connection.commit()

            app.current_user['pseudo'] = pseudo
            app.current_user['icon'] = selected_icon

            app.switch_to_main_screen()
        except Exception as e:
            print(f"Error saving profile: {e}")
            app.show_snackbar(app.get_translation("Error saving profile. Please try again."))

    def open_menu(self, button):
        app = MDApp.get_running_app()

        menu_items = [
            {
                "height": dp(56),
                "leading_icon": "theme-light-dark",
                "text": self.change_theme_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.change_theme_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "email",
                "text": self.contact_support_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.contact_support_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "translate",
                "text": self.languages_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.languages_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "logout",
                "text": self.deconnect_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.deconnect_text: self.menu_callback(x),
            }
        ]

        if not self.menu or self.menu.caller != button:
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.menu.open()

    # Fonction de modifications des items au sein des menus
    def menu_callback(self, text_item):
        app = MDApp.get_running_app()
        if text_item == self.change_theme_text:
            self.change_theme()
        elif text_item == self.contact_support_text:
            app.contact_support()
        elif text_item == self.deconnect_text:
            app.disconnect()
        elif text_item == self.languages_text:
            # Toggle between English and French
            app.current_language = 'fr' if app.current_language == 'en' else 'en'
            # Switch to changing language screen
            app.switch_to_changing_screen(self)
        self.menu.dismiss()

    # Fonction de mofication du thème
    def change_theme(self):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = (
            "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        )
"""
####################################
####### Ecran de chargement ########
####################################
"""

class LoadingScreen(MDScreen):
    loading_text= StringProperty()
    competition_created_successfully_text = StringProperty()
    competition_joined_successfully_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.loading_text = app.get_translation("Loading...")
        self.competition_created_successfully_text = app.get_translation("Competition created successfully")
        self.competition_joined_successfully_text = app.get_translation("Joined competition successfully")


"""
##############################################
####### Ecran de changement de langue ########
##############################################
"""

class ChangingLanguageScreen(MDScreen):
    changing_language_text= StringProperty()

    def __init__(self, previous_screen_type=None, **kwargs):
        super().__init__(**kwargs)
        self.previous_screen_type = previous_screen_type
        self.app = MDApp.get_running_app()
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.changing_language_text = app.get_translation("Changing Language...")

"""
####################################
####### Ecran de modif mdp  ########
####################################
"""

class ForgotPasswordScreen(MDScreen):
    forgot_your_password_text = StringProperty()
    email_adress_text = StringProperty()
    send_temporary_password_text = StringProperty()
    enter_temporary_password_text = StringProperty()
    enter_new_password_text = StringProperty()
    confirm_new_password_text = StringProperty()
    confirm_changes_text =StringProperty()
    cancel_text = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.forgot_your_password_text = app.get_translation("Forgot your password ?")
        self.email_adress_text = app.get_translation("Email")
        self.send_temporary_password_text = app.get_translation("Send temporary password")
        self.enter_temporary_password_text = app.get_translation("Enter temporary password")
        self.enter_new_password_text = app.get_translation("Enter new password")
        self.confirm_new_password_text = app.get_translation("Confirm new password")
        self.confirm_changes_text = app.get_translation("Confirm changes")
        self.cancel_text = app.get_translation("Cancel")

    def change_password(self):
        email = self.ids.current_email.text
        temp_password = self.ids.temporary_password.text
        new_password = self.ids.new_password.text
        confirm_new_password = self.ids.confirm_new_password.text

        if not email or not temp_password or not new_password or not confirm_new_password:
            self.app.show_snackbar(self.app.get_translation("Please fill in all fields"))
            return

        if new_password != confirm_new_password:
            self.app.show_snackbar(self.app.get_translation("New passwords do not match"))
            return

        try:
            self.app.secure_storage.validate_password(new_password)
            self.app.change_password(email, temp_password, new_password, confirm_new_password)
        except ValueError as e:
            self.app.show_snackbar(str(e))

    def send_temporary_password(self):
        app = MDApp.get_running_app()
        email = self.ids.current_email.text
        if not email:
            self.app.show_snackbar(app.get_translation("Please enter your email address"))
            return

        self.app.handle_forgot_password(email)

# Ecran de modification du mot de passe si souhaité
# -------------------------------------------------
class ChangePasswordScreen(MDScreen):
    change_password_text = StringProperty()
    current_password_text = StringProperty()
    new_password_text= StringProperty()
    confirm_new_password_text = StringProperty()
    cancel_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.change_password_text = app.get_translation("Change Password")
        self.current_password_text = app.get_translation("Current Password")
        self.new_password_text = app.get_translation("New Password")
        self.confirm_new_password_text = app.get_translation("Confirm new password")
        self.cancel_text = app.get_translation("Cancel")

    def change_password(self):
        app = MDApp.get_running_app()
        current_password = self.ids.current_password.text
        new_password = self.ids.new_password.text
        confirm_password = self.ids.confirm_password.text

        if not current_password or not new_password or not confirm_password:
            app.show_snackbar(app.get_translation("Please fill in all fields"))
            return

        if new_password != confirm_password:
            app.show_snackbar(app.get_translation("New passwords do not match"))
            return

        try:
            app.secure_storage.validate_password(new_password)
        except ValueError as e:
            app.show_snackbar(str(e))
            return

        # Verify current password
        stored_password = app.secure_storage.get_password(app.current_user['email'])
        if not app.secure_storage.verify_password(stored_password, current_password):
            app.show_snackbar(app.get_translation("Current password is incorrect"))
            return

        try:
            hashed_password = app.secure_storage.hash_password(new_password)
            app.secure_storage.store_password(app.current_user['email'], hashed_password)
            app.show_snackbar(app.get_translation("Password changed successfully"))
            app.switch_to_main_screen()
        except Exception as e:
            app.show_snackbar(app.get_translation("Error changing password. Please try again."))
            print(f"Error changing password: {str(e)}")


"""
#############################################
####### Ecran de verification email  ########
#############################################
"""

class VerificationPendingScreen(MDScreen):
    email = StringProperty("")
    please_verify_your_email_text = StringProperty()
    enter_digit_text =StringProperty()
    verification_code_sent_text = StringProperty()
    verify_text = StringProperty()
    resend_verification_email_text=StringProperty()
    cancel_text= StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.please_verify_your_email_text = app.get_translation("Please verify your email")
        self.enter_digit_text = app.get_translation("Enter 6-digit code")
        self.verification_code_sent_text = app.get_translation("A verification code has been sent to the email address {}")
        self.verify_text = app.get_translation("Verify")
        self.resend_verification_email_text = app.get_translation("Resend Verification Email")
        self.cancel_text = app.get_translation("Cancel")

    def verify_code(self):
        app = MDApp.get_running_app()
        entered_code = self.ids.verification_code.text
        if app.current_user and 'email' in app.current_user:
            email = app.current_user['email']
            app.verify_email_code(email, entered_code)
        else:
            app.show_snackbar(app.get_translation("Error: User data not found."))

    def resend_verification_email(self):
        app = MDApp.get_running_app()
        if app.current_user and 'email' in app.current_user:
            email = app.current_user['email']
            app.resend_verification_email(email)
        else:
            app.show_snackbar(app.get_translation("Error: User data not found."))

"""
#################################
####### Ecran d'accueil ########
#################################
"""

class HomeScreen(MDScreen):
    verify_text = StringProperty()
    change_theme_text = StringProperty()
    languages_text = StringProperty()
    deconnect_text = StringProperty()
    contact_support_text = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = None
        self.panels_added = False
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.verify_text = app.get_translation("Verify")
        self.change_theme_text = app.get_translation("Change Theme")
        self.languages_text = app.get_translation("Languages")
        self.deconnect_text = app.get_translation("Deconnect")
        self.contact_support_text = app.get_translation("Contact Support")

    def on_enter(self):
        if not self.panels_added:
            Clock.schedule_once(self.add_expansion_panels, 0)
            self.panels_added = True

    def add_expansion_panels(self, dt):
        async def set_panel_list():
            await asynckivy.sleep(0)
            container = self.ids.container
            container.clear_widgets()
            container.add_widget(ExpansionPanelItemConnection())
            container.add_widget(ExpansionPanelItemInscription())
            container.add_widget(ExpansionPanelItemVerification())
        asynckivy.start(set_panel_list())

    def open_menu(self, button):
        menu_items = [
            {
                "height": dp(56),
                "leading_icon": "theme-light-dark",
                "text": self.change_theme_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.change_theme_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "email",
                "text": self.contact_support_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.contact_support_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "translate",
                "text": self.languages_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.languages_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "logout",
                "text": self.deconnect_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.deconnect_text: self.menu_callback(x),
            }
        ]

        if not self.menu or self.menu.caller != button:
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.menu.open()

    # Fonction de modifications des items aux seins des menus
    def menu_callback(self, text_item):
        app = MDApp.get_running_app()
        if text_item == self.change_theme_text:
            self.change_theme()
        elif text_item == self.contact_support_text:
            app.contact_support()
        elif text_item == self.deconnect_text:
            app.disconnect()
        elif text_item == self.languages_text:
            # Toggle between English and French
            app.current_language = 'fr' if app.current_language == 'en' else 'en'
            # Switch to changing language screen
            app.switch_to_changing_screen(self)
        self.menu.dismiss()

    #Fonction de mofication du thème
    def change_theme(self):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = (
            "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        )

"""
#################################
####### Ecran principal #########
#################################
"""

class MainScreen(MDScreen):
    home_menu_text = StringProperty()
    manage_text = StringProperty()
    change_theme_text = StringProperty()
    languages_text = StringProperty()
    deconnect_text = StringProperty()
    contact_support_text = StringProperty()
    setup_your_profile_text = StringProperty()
    modify_password_text = StringProperty()
    competition_created_successfully_text = StringProperty()
    competition_joined_successfully_text = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = None
        self.competitions = []
        self.preloaded_screens = {}
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.home_menu_text = app.get_translation("HomeMenu")
        self.manage_text = app.get_translation("Manage")
        self.change_theme_text = app.get_translation("Change Theme")
        self.languages_text = app.get_translation("Languages")
        self.deconnect_text = app.get_translation("Deconnect")
        self.contact_support_text = app.get_translation("Contact Support")
        self.setup_your_profile_text = app.get_translation("Setup your profile")
        self.modify_password_text = app.get_translation("Modify password")
        self.competition_created_successfully_text = app.get_translation("Competition created successfully")
        self.competition_joined_successfully_text = app.get_translation("Joined competition successfully")

    #Initialisation
    profile_icon_source = StringProperty("account-circle-outline")
    pseudo = StringProperty("User")  # Default pseudo

    # Chargement des données utilisateurs depuis le users.json file
    # -------------------------------------------------------------
    def load_user_data(self, *args):
        app = MDApp.get_running_app()
        if app.current_user:
            try:
                with app.db_connection:
                    with app.db_connection.cursor() as cursor:
                        cursor.execute("SELECT * FROM users WHERE email = %s", (app.current_user['email'],))
                        user_data = cursor.fetchone()
                        if user_data:
                            self.pseudo = user_data.get('pseudo', 'User')
                            self.profile_icon_source = user_data.get('icon', 'account-circle-outline')

                            # Update app.current_user with the latest data
                            app.current_user.update(user_data)

                # Update the UI elements
                if hasattr(self.ids, 'pseudo_label'):
                    self.ids.pseudo_label.text = self.pseudo
                if hasattr(self.ids, 'profile_icon'):
                    self.ids.profile_icon.icon = self.profile_icon_source
                if hasattr(self.ids, 'user_icon'):
                    self.ids.user_icon.icon = self.profile_icon_source

            except Exception as e:
                print(f"Error loading user data: {e}")
                MDSnackbar(MDSnackbarText(text=app.get_translation("Error loading user data. Please try again."))).open()
                # Ensure the connection is reset
                app.db_connection.rollback()

    # Ouverture et configuration du menu de la TopAppBar de l'écran principal
    # -----------------------------------------------------------------------
    def open_menu(self, button):
        app = MDApp.get_running_app()

        menu_items = [
            {
                "height": dp(56),
                "leading_icon": "theme-light-dark",
                "text": self.change_theme_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.change_theme_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "email",
                "text": self.contact_support_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.contact_support_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "translate",
                "text": self.languages_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.languages_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "logout",
                "text": self.deconnect_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.deconnect_text: self.menu_callback(x),
            }
        ]

        if not self.menu or self.menu.caller != button:
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.menu.open()

    # Ouverture et configuration du profil
    # ------------------------------------
    def open_profil(self, button):
        if not self.menu or self.menu.caller != button:
            menu_items = [
                {
                    "height": dp(56),
                    "text": self.setup_your_profile_text,
                    "trailing_icon": "chevron-right",
                    "on_release": lambda x="Setup": self.handle_profile_action(x),
                },
                {
                    "height": dp(56),
                    "text": self.modify_password_text,
                    "trailing_icon": "chevron-right",
                    "on_release": lambda x="Password": self.handle_profile_action(x),
                },
            ]
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.menu.open()

    # Modification des éléments dans les menus "menu" et "profil"
    # -------------------------------------------------------------
    def menu_callback(self, text_item):
        app = MDApp.get_running_app()
        if text_item == self.change_theme_text:
            self.change_theme()
        elif text_item == self.contact_support_text:
            app.contact_support()
        elif text_item == self.deconnect_text:
            app.disconnect()
        elif text_item == self.languages_text:
            # Toggle between English and French
            app.current_language = 'fr' if app.current_language == 'en' else 'en'
            # Switch to changing language screen
            app.switch_to_changing_screen(self)
        self.menu.dismiss()

    # Accès aux éléments de profil
    # ----------------------------
    def handle_profile_action(self, action):
        app = MDApp.get_running_app()
        if action == "Setup":
            app.switch_to_setup_profile()
        elif action == "Password":
            app.switch_to_change_password_screen()
        self.menu.dismiss()

    #Fonction de modification du thème
    # --------------------------------
    def change_theme(self):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = (
            "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        )

# ----------------------------------
# -- Bottom Navigation Bar
# ----------------------------------

    #Fonction de swipe des écrans de la navigation bar
    def on_switch_tabs(self, bar: MDNavigationBar, item: MDNavigationItem, item_icon: str, item_text: str):
        self.ids.screen_manager.current = item_text

# ----------------------------------
# -- NavigationRail
# ----------------------------------

    # Fonction d'accès au MainHome
    # ----------------------------
    def show_main_home(self, *args):
        main_home = MainHome(name='main_home')
        self.ids.competition_manager.add_widget(main_home)
        self.ids.competition_manager.current = 'main_home'

    # Fonction de chargement des compétitions du user depuis le users.json file
    # ------------------------------------------------------------------------
    def load_competitions(self, *args):
        app = MDApp.get_running_app()
        self.competitions = []  # Clear existing competitions

        with app.db_connection.cursor() as cursor:
            cursor.execute("""
            SELECT c.*, uc.points
            FROM competitions c
            JOIN user_competitions uc ON c.competition_id = uc.competition_id
            WHERE uc.user_id = %s
            """, (app.current_user['email'],))
            competitions = cursor.fetchall()

            for competition in competitions:
                competition_id = competition['competition_id']
                competition_name = competition['name']
                competition_type = competition['type']

                # Create a dictionary with competition details
                competition_details = {
                    'id': competition_id,
                    'name': competition_name,
                    'type': competition_type,
                    'points': competition['points'],
                    'rules': json.loads(competition['rules']) if isinstance(competition['rules'], str) else competition['rules']
                }

                # Add to self.competitions without duplicates
                if competition_id not in [comp['id'] for comp in self.competitions]:
                    self.competitions.append(competition_details)

                    # Preload the competition screen
                    screen_name = f"competition_{competition_id}"
                    if screen_name not in self.preloaded_screens:
                        new_screen = self.create_competition_screen(competition_type, screen_name, competition_name,
                                                                    competition_id)
                        self.preloaded_screens[screen_name] = new_screen

        # After loading all competitions, update the navigation rail
        self.update_navigation_rail()

    # Fonction de mise à jour du navigation rail
    def update_navigation_rail(self):
        nav_rail = self.ids.nav_rail
        # Try different methods to remove competition items
        for item in list(nav_rail.get_items()):
            if hasattr(item, 'competition_details'):
                if item.competition_details['id'] not in [comp['id'] for comp in self.competitions]:
                    # Method 3: parent.remove_widget
                    if item.parent:
                        item.parent.remove_widget(item)
                        # print(f"Tried parent.remove_widget on: {item.competition_details['id']}")

        # Add new competitions
        for competition in self.competitions:
            existing_item = next((item for item in nav_rail.get_items() if
                                  hasattr(item, 'competition_details') and item.competition_details['id'] ==
                                  competition['id']), None)
            if not existing_item:
                self.add_competition_to_rail(competition)
                # print(f"Added competition to navigation rail: {competition['id']}")
            elif existing_item.opacity == 0 or existing_item.disabled:
                existing_item.opacity = 1
                existing_item.disabled = False
                # print(f"Re-enabled existing item: {competition['id']}")

        # print("Navigation rail items after update:")
        for item in nav_rail.get_items():
            if hasattr(item, 'competition_details'):
                print(
                    f"- ID: {item.competition_details['id']}, Name: {item.competition_details['name']}, Opacity: {item.opacity}, Disabled: {item.disabled}")
            else:
                label = item.children[1].text if len(item.children) > 1 else "No label"
                print(f"- Label: {label}")

    # Fonction d'ajout d'une nouvelle compétition au rail
    def add_competition_to_rail(self, competition_details):
        nav_rail = self.ids.nav_rail

        # Check if the competition already exists in the rail
        for item in nav_rail.get_items():
            if hasattr(item, 'competition_details') and item.competition_details['id'] == competition_details['id']:
                # print(f"Competition {competition_details['id']} already in NavigationRail. Skipping.")
                return

        new_item = MDNavigationRailItem()
        new_item._navigation_rail = nav_rail  # Set the navigation rail reference

        icon = MDNavigationRailItemIcon(icon="trophy-outline")
        icon._navigation_rail = nav_rail  # Set the navigation rail reference for the icon
        icon._navigation_item = new_item  # Set the navigation item reference for the icon
        new_item.add_widget(icon)

        label = MDNavigationRailItemLabel(text=competition_details['name'])
        new_item.add_widget(label)

        new_item.pos_hint = {"center_x": 0.5, "center_y": 0.9}

        # Store the competition details in the item for later use
        new_item.competition_details = competition_details

        # Bind the on_active event to a lambda function that checks the active state
        new_item.bind(active=lambda instance, value: self.on_nav_rail_item_active(instance) if value else None)

        nav_rail.add_widget(new_item)

    # Fonction d'accès au ManageCompetitionScreen
    # ------------------------------------------
    def show_manage_competition_screen(self):
        # print("show_add_competition_screen called")
        app = MDApp.get_running_app()
        app.switch_to_manage_competition_screen()

    # Fonction d'activation des items du NavigationRail
    # ------------------------------------------------

    def on_nav_rail_item_active(self, instance_navigation_rail_item):
        app = MDApp.get_running_app()
        nav_rail = self.ids.nav_rail
        items = nav_rail.get_items()
        total_items = len(items)
        index = total_items - items.index(instance_navigation_rail_item) - 1
        # print(f"Index: {index}")

        if index == 0:  # Home (now the last item)
            self.show_main_home()
        elif index == 1:  # Add Competition (now the second to last item)
            self.show_manage_competition_screen()
        else:
            competition_details = next((comp for comp in self.competitions if comp['id'] == instance_navigation_rail_item.competition_details['id']), None)
            if competition_details:
                competition_id = competition_details['id']
                screen_name = f"competition_{competition_id}"
                if screen_name not in self.ids.competition_manager.screen_names:
                    if screen_name in self.preloaded_screens:
                        new_screen = self.preloaded_screens[screen_name]
                    else:
                        new_screen = self.create_competition_screen(competition_details['type'], screen_name, competition_details['name'], competition_id)
                        self.preloaded_screens[screen_name] = new_screen
                    self.ids.competition_manager.add_widget(new_screen)
                self.ids.competition_manager.current = screen_name
                # print(f"Switched to {screen_name} with competition_id: {competition_id}")
            else:
                print(f"Competition details not found for the selected item")

    # Fonction de "création" d'un CompétitionScreen, pour l'longlet Pronostics
    def create_competition_screen(self, competition_type, screen_name, competition_name, competition_id):
        if competition_type == "Ligue Magnus":
            return CompetitionScreenLM(name=screen_name, competition_name=competition_name, competition_id=competition_id)
        elif competition_type == "NL":
            return CompetitionScreenNL(name=screen_name, competition_name=competition_name, competition_id=competition_id)
        elif competition_type == "Four Nations":
            return CompetitionScreenFourNations(name=screen_name, competition_name=competition_name, competition_id=competition_id)

"""
#################################
####### Ecran d'accueil #########
#################################
"""

class MainHome(MDScreen):
    welcome_text = StringProperty()
    to_text = StringProperty()
    bet_here_text = StringProperty()
    ligue_magnus_text = StringProperty()
    nl_text = StringProperty()
    nhl_text= StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.welcome_text = app.get_translation("Welcome")
        self.to_text = app.get_translation("to")
        self.bet_here_text = app.get_translation("Bet here with your friends on multiple hockey leagues :")
        self.ligue_magnus_text = app.get_translation("French Ligue Magnus")
        self.nl_text = app.get_translation("Swiss National League")
        self.nhl_text = app.get_translation("NHL Four Nations Tournament")
"""
########################################
####### CompetitionScreen & Co #########
####### NavigationBar : Pronostics  ####
########################################
"""

# - PredictionsMethod : WinnerLoser
#----------------------------------

class MatchWidgetWinnerLoser(MDBoxLayout):
    date = StringProperty()
    journee = StringProperty()
    team1 = StringProperty()
    team2 = StringProperty()
    team1_extra = StringProperty()
    team2_extra = StringProperty()
    team1_icon = StringProperty()
    team2_icon = StringProperty()
    is_draw_selected = BooleanProperty(False)
    team1_odds = StringProperty()
    team2_odds = StringProperty()
    draw_odds = StringProperty()
    team1_extra_odds = StringProperty()
    team2_extra_odds = StringProperty()
    show_odds = BooleanProperty(False)
    selected_outcome = ObjectProperty(None, allownone=True)
    team1_selected = BooleanProperty(False)
    team2_selected = BooleanProperty(False)
    draw_selected = BooleanProperty(False)
    team1_extra_selected = BooleanProperty(False)
    team2_extra_selected = BooleanProperty(False)
    team1_style = StringProperty("elevated")
    team2_style = StringProperty("elevated")
    team1_extra_style = StringProperty("elevated")
    team2_extra_style = StringProperty("elevated")
    winner_in_extra_time_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_bet_placed')
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.winner_in_extra_time_text = app.get_translation("Winner in extra time")

    def on_bet_placed(self, *args):
        pass

    def select_outcome(self, outcome):
        if outcome in ['team1', 'team2']:
            self.is_draw_selected = False
        elif outcome in ['team1_extra', 'team2_extra']:
            self.is_draw_selected = True

        self.team1_selected = outcome == 'team1'
        self.team2_selected = outcome == 'team2'
        self.team1_extra_selected = outcome == 'team1_extra'
        self.team2_extra_selected = outcome == 'team2_extra'
        self.selected_outcome = outcome

        # Update button styles
        self.team1_style = "filled" if self.team1_selected else "elevated"
        self.team2_style = "filled" if self.team2_selected else "elevated"
        self.team1_extra_style = "filled" if self.team1_extra_selected else "elevated"
        self.team2_extra_style = "filled" if self.team2_extra_selected else "elevated"

        self.dispatch('on_bet_placed')

    def select_team1(self):
        self.select_outcome('team1')

    def select_team2(self):
        self.select_outcome('team2')

    def select_draw(self):
        self.select_outcome('draw')

    def select_team1_extra(self):
        self.select_outcome('team1_extra')

    def select_team2_extra(self):
        self.select_outcome('team2_extra')

    def toggle_draw(self):
        if self.is_draw_selected:
            # If draw was selected, unselect it and clear any extra time selection
            self.is_draw_selected = False
            self.selected_outcome = None
            self.team1_extra_style = "elevated"
            self.team2_extra_style = "elevated"
        else:
            # If draw was not selected, select it and clear any regular time selection
            self.is_draw_selected = True
            if self.selected_outcome in ['team1', 'team2']:
                self.selected_outcome = None
            self.team1_style = "elevated"
            self.team2_style = "elevated"

        self.dispatch('on_bet_placed')

# Predictions Method: MatchScore
# ------------------------------

class MatchWidgetMatchScore(MDBoxLayout):
    date = StringProperty()
    journee = StringProperty()
    team1 = StringProperty()
    team2 = StringProperty()
    team1_icon = StringProperty()
    team2_icon = StringProperty()
    team1_score = StringProperty('1')
    team2_score = StringProperty('0')
    is_draw_selected = BooleanProperty(False)
    selected_outcome = ObjectProperty(None, allownone=True)
    team1_style = StringProperty("elevated")
    team2_style = StringProperty("elevated")
    team1_extra_style = StringProperty("elevated")
    team2_extra_style = StringProperty("elevated")
    winner_in_extra_time_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_bet_placed')
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.winner_in_extra_time_text = app.get_translation("Winner in extra time")

    def on_bet_placed(self, *args):
        pass

    def select_outcome(self, outcome):
        print(f"select_outcome called with: {outcome}")
        self.is_draw_selected = False
        self.team1_style = "elevated"
        self.team2_style = "elevated"
        self.team1_extra_style = "elevated"
        self.team2_extra_style = "elevated"

        if isinstance(outcome, dict):
            # Handle the bet dictionary format
            self.team1_score, self.team2_score = outcome['score'].split('-')
            if outcome['winner'] == 'team1':
                self.team1_style = "filled"
            elif outcome['winner'] == 'team2':
                self.team2_style = "filled"
            elif outcome['winner'] == 'draw':
                self.is_draw_selected = True
            elif outcome['winner'] == 'team1_extra':
                self.is_draw_selected = True
                self.team1_extra_style = "filled"
            elif outcome['winner'] == 'team2_extra':
                self.is_draw_selected = True
                self.team2_extra_style = "filled"
        else:
            # Handle the existing string-based outcome
            if outcome is None:
                self.team1_score = '1'
                self.team2_score = '0'
            elif '-' in outcome:  # It's a score
                self.team1_score, self.team2_score = outcome.split('-')
                if int(self.team1_score) > int(self.team2_score):
                    self.team1_style = "filled"
                elif int(self.team2_score) > int(self.team1_score):
                    self.team2_style = "filled"
            elif outcome in ['team1_extra', 'team2_extra']:
                self.is_draw_selected = True
                if outcome == 'team1_extra':
                    self.team1_extra_style = "filled"
                else:
                    self.team2_extra_style = "filled"
            elif outcome == 'draw':
                self.is_draw_selected = True
                self.team1_score = '0'
                self.team2_score = '0'

        self.selected_outcome = outcome
        self.dispatch('on_bet_placed')

    def update_bet(self):
        bet = {'score': f"{self.team1_score}-{self.team2_score}"}

        if int(self.team1_score) == int(self.team2_score):
            self.is_draw_selected = True
            bet['winner'] = 'draw'
            self.team1_style = "elevated"
            self.team2_style = "elevated"
        else:
            self.is_draw_selected = False
            if int(self.team1_score) > int(self.team2_score):
                bet['winner'] = 'team1'
                self.team1_style = "filled"
                self.team2_style = "elevated"
            else:
                bet['winner'] = 'team2'
                self.team1_style = "elevated"
                self.team2_style = "filled"

        if self.is_draw_selected:
            if self.selected_outcome == 'team1_extra':
                bet['winner'] = 'team1_extra'
            elif self.selected_outcome == 'team2_extra':
                bet['winner'] = 'team2_extra'

        self.selected_outcome = bet
        self.dispatch('on_bet_placed')

    def select_team1_extra(self):
        self.selected_outcome = 'team1_extra'
        self.team1_extra_style = "filled"
        self.team2_extra_style = "elevated"
        self.dispatch('on_bet_placed')

    def select_team2_extra(self):
        self.selected_outcome = 'team2_extra'
        self.team1_extra_style = "elevated"
        self.team2_extra_style = "filled"
        self.dispatch('on_bet_placed')

    def increment_score(self, team):
        if team == 1:
            self.team1_score = str(int(self.team1_score) + 1)
        else:
            self.team2_score = str(int(self.team2_score) + 1)
        self.selected_outcome = None  # Reset extra time selection
        self.update_bet()

    def decrement_score(self, team):
        if team == 1:
            self.team1_score = str(max(0, int(self.team1_score) - 1))
        else:
            self.team2_score = str(max(0, int(self.team2_score) - 1))
        self.selected_outcome = None  # Reset extra time selection
        self.update_bet()

    def on_team1_score(self, instance, value):
        self.update_bet()

    def on_team2_score(self, instance, value):
        self.update_bet()

    def toggle_draw(self):
        if self.is_draw_selected:
            # If draw was selected, unselect it and clear any extra time selection
            self.is_draw_selected = False
            self.selected_outcome = f"{self.team1_score}-{self.team2_score}"
            self.team1_extra_style = "elevated"
            self.team2_extra_style = "elevated"
        else:
            # If draw was not selected, select it and set scores to equal values
            self.is_draw_selected = True
            self.selected_outcome = 'draw'
            # Set both scores to the same value (e.g., the higher of the two current scores)
            max_score = max(int(self.team1_score), int(self.team2_score))
            self.team1_score = str(max_score)
            self.team2_score = str(max_score)

        self.team1_style = "elevated"
        self.team2_style = "elevated"
        self.update_bet()
        self.dispatch('on_bet_placed')


"""
########################################
####### CompetitionScreen & Co #########
####### NavigationBar : Rankings #######
########################################
"""

class RankingsCard(MDCard):
    rank = StringProperty()
    team = StringProperty()
    points = StringProperty()

    def __init__(self, rank, team, points, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.rank = rank
        self.team = team
        self.points = points
        # self.padding = "20dp"
        # self.spacing = "20dp"

"""
########################################
####### CompetitionScreen & Co #########
####### NavigationBar : Pronostics  ####
########################################
"""

class CompetitionScreenLM(MDScreen):
    competition_name = StringProperty("")
    competition_id = StringProperty("")
    unsaved_bets_count = NumericProperty(0)
    pronostics_text = StringProperty()
    rankings_text = StringProperty()
    league_rankings_text = StringProperty()
    no_matches_available_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.competition_name = kwargs.get('competition_name', '')
        self.competition_id = kwargs.get('competition_id', '')
        self.app = MDApp.get_running_app()
        self.rankings_loaded = False
        self.user_bets = {}
        self.unsaved_bets = set()
        # print(f"CompetitionScreenLM initialized with competition_id: {self.competition_id}")

        # Load rankings data once
        self.load_rankings()
        # Load matches data once
        self.load_matches()
        # Translations
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.pronostics_text = app.get_translation("Pronostics")
        self.rankings_text = app.get_translation("Rankings")
        self.league_rankings_text = app.get_translation("League Rankings")
        self.no_matches_available_text = app.get_translation("No matches available yet. Check back later when the playoffs begin.")

    def on_enter(self):
        super().on_enter()
        self.calculate_and_save_points()
        self.update_classement()

    def update_classement(self):
        classement_screen = self.ids.screen_manager.get_screen('rankings')
        if not hasattr(classement_screen.ids, 'classement_content'):
            print("Error: classement_content not found in Classement screen")
            return

        classement_content = classement_screen.ids.classement_content
        classement_content.clear_widgets()

        try:
            with self.app.db_connection.cursor() as cursor:
                cursor.execute("""
                SELECT u.pseudo, uc.points, u.icon
                FROM user_competitions uc
                JOIN users u ON uc.user_id = u.user_id
                WHERE uc.competition_id = %s
                ORDER BY uc.points DESC
                """, (self.competition_id,))
                user_points = cursor.fetchall()
                print(f"user_points: {user_points}")

            if not user_points:
                classement_content.add_widget(MDLabel(text="No users in this competition yet.", size_hint_x=1))
                return

            for rank, user_data in enumerate(user_points, start=1):
                pseudo = user_data['pseudo']
                points = user_data['points']
                icon= user_data['icon']

                row_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", spacing="10dp")
                row_layout.add_widget(MDLabel(text=str(rank), size_hint_x=0.5))
                user_box = MDBoxLayout(orientation="horizontal", size_hint_x=1.8, pos_hint={"center_x": 0.5, "top": 0.95})
                user_box.add_widget(MDIconButton(icon=icon if icon else "account", size_hint_x=0.2, pos_hint={"center_x": 0.5, "top": 1}))
                user_box.add_widget(MDLabel(text=pseudo or "Unknown", valign="center"))
                row_layout.add_widget(user_box)
                row_layout.add_widget(MDLabel(text=str(points), size_hint_x=0.8))
                classement_content.add_widget(row_layout)

        except Exception as e:
            print(f"Error updating classement: {e}")
            classement_content.add_widget(MDLabel(text="Error loading ranking. Please try again later.", size_hint_x=1))

    def load_matches(self):
        app = MDApp.get_running_app()
        quotes_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/quotes_LM.csv"
        quotes_response = requests.get(quotes_url)
        if quotes_response.status_code == 200:
            quotes_data = {}
            csv_content = StringIO(quotes_response.text)
            csv_reader = csv.DictReader(csv_content)
            for row in csv_reader:
                date = row['date']
                match = row['match']
                if date not in quotes_data:
                    quotes_data[date] = {}
                quotes_data[date][match] = {
                    'team1': float(row['team1']),
                    'team2': float(row['team2']),
                    'draw': float(row['draw']),
                    'team1_extra': float(row['team1_extra']),
                    'team2_extra': float(row['team2_extra'])
                }
        else:
            quotes_data = {}
        competition_data = self.app.load_competition(self.competition_id)
        if competition_data and "upcoming_matches" in competition_data:
            upcoming_matches = competition_data["upcoming_matches"]
            user_bets = self.app.load_user_bets(self.app.current_user['email'], self.competition_id)
            print(f"User bets: {user_bets}")
            predictions_method = competition_data.get("predictions_method", "winner_loser")
            awarding_points_method = competition_data.get("awarding_points_method", "point_scale")

            # Extract point_scale from rules
            rules = competition_data.get('rules', {})
            if isinstance(rules, str):
                rules = json.loads(rules)
            point_scale = rules.get('point_scale', {})

            # Set default values if not present
            default_point_scale = {
                'winner': 3,
                'winner_ot': 2,
                'loser_ot': 1,
                'loser': 0
            }
            for key, value in default_point_scale.items():
                if key not in point_scale:
                    point_scale[key] = value

            pronostics_screen = self.ids.screen_manager.get_screen('pronostics')
            matches_layout = pronostics_screen.ids.matches_layout
            matches_layout.clear_widgets()

            if not upcoming_matches:
                no_matches_label = MDLabel(
                    text=app.get_translation("No matches available yet. Check back later when the playoffs begin."),
                    halign="center",
                    adaptive_size=True,
                    theme_text_color="Secondary"
                )
                matches_layout.add_widget(no_matches_label)
            else:
                for match in upcoming_matches:
                    if predictions_method == "winner_loser":
                        match_widget = MatchWidgetWinnerLoser()
                    else:
                        match_widget = MatchWidgetMatchScore()

                    match_date = pd.to_datetime(match['date']).date()
                    match_widget.date = match_date.strftime('%d/%m/%Y')
                    comparison_date = match_date.strftime('%Y-%m-%d')
                    match_widget.journee = f"Journée {match['journee']}"
                    team1, team2 = match['match'].split(' - ')
                    match_widget.team1 = team1
                    match_widget.team2 = team2
                    match_widget.team1_icon = self.app.team_icons.get(team1, "hockey-puck")
                    match_widget.team2_icon = self.app.team_icons.get(team2, "hockey-puck")

                    if awarding_points_method == "bookmaker_quotes":
                        formatted_date = match_date.strftime('%Y-%m-%d')
                        match_id = f"{team1} - {team2}"

                        if formatted_date in quotes_data and match_id in quotes_data[formatted_date]:
                            quotes = quotes_data[formatted_date][match_id]
                        else:
                            # Use default quotes if not found in the CSV data
                            quotes = {
                                'team1': 2.0,
                                'team2': 2.0,
                                'draw': 3.0,
                                'team1_extra': 4.0,
                                'team2_extra': 4.0
                            }

                        match_widget.team1_odds = str(quotes['team1'])
                        match_widget.team2_odds = str(quotes['team2'])
                        match_widget.draw_odds = str(quotes['draw'])
                        match_widget.team1_extra_odds = str(quotes['team1_extra'])
                        match_widget.team2_extra_odds = str(quotes['team2_extra'])
                        match_widget.show_odds = True

                    elif awarding_points_method == "point_scale":
                        match_widget.winner_points = point_scale['winner']
                        match_widget.winner_ot_points = point_scale['winner_ot']
                        match_widget.loser_ot_points = point_scale['loser_ot']
                        match_widget.loser_points = point_scale['loser']
                        match_widget.show_odds = False

                    match_id = f"{match_widget.team1} - {match_widget.team2}"

                    print(f"Match date: {match_widget.date}, Comparison date: {comparison_date}, Match ID: {match_id}")
                    print(f"Condition met: {comparison_date in user_bets and match_id in user_bets[comparison_date]}")

                    if comparison_date in user_bets and match_id in user_bets[comparison_date]:
                        print(f"Calling select_outcome with: {user_bets[comparison_date][match_id]}")
                        match_widget.select_outcome(user_bets[comparison_date][match_id])

                    match_widget.bind(selected_outcome=lambda instance, value: self.on_bet_placed(instance))
                    matches_layout.add_widget(match_widget)

                    if comparison_date not in user_bets or match_id not in user_bets[comparison_date]:
                        self.add_unsaved_bet(match_id)
                    match_widget.bind(selected_outcome=lambda instance, value: self.on_bet_placed(instance))
                    self.count_unsaved_bets()

    def count_unsaved_bets(self):
        self.unsaved_bets_count = len(self.unsaved_bets)

    def on_bet_placed(self, match_widget):
        match_id = f"{match_widget.team1} - {match_widget.team2}"
        date = match_widget.date
        bet = match_widget.selected_outcome

        # Ensure the date is in the correct format (DD/MM/YYYY)
        try:
            formatted_date = datetime.strptime(date, '%d/%m/%Y').strftime('%d/%m/%Y')
        except ValueError:
            print(f"Error: Invalid date format: {date}")
            return

        self.app.save_user_bets(
            self.app.current_user['email'],
            self.competition_id,
            formatted_date,
            {match_id: bet}
        )

        # Remove the saved bet from unsaved_bets
        self.unsaved_bets.discard(match_id)
        self.count_unsaved_bets()

    def add_unsaved_bet(self, match_id):
        self.unsaved_bets.add(match_id)
        self.count_unsaved_bets()

    def calculate_and_save_points(self):
        competition_data = self.app.load_competition(self.competition_id)
        predictions_method = competition_data.get("predictions_method", "winner_loser")
        awarding_points_method = competition_data.get("awarding_points_method", "point_scale")

        if predictions_method == "match_score":
            point_scale = competition_data.get("point_scale", {
                "good_goal_difference": 1,
                "exact_score_regular": 4,
                "exact_score_extra": 3,
                "winner_regular": 2,
                "winner_extra": 1,
                "loser_regular": 0,
                "loser_extra": 0
            })
        else:
            point_scale = competition_data.get("point_scale", {
                'winner': 3,
                'winner_ot': 2,
                'loser_ot': 1,
                'loser': 0
            })

        print(f"Calculating points for competition {self.competition_id}")
        print(f"Predictions method: {predictions_method}")
        print(f"Awarding points method: {awarding_points_method}")

        total_points = 0
        user_bets = self.app.load_user_bets(self.app.current_user['email'], self.competition_id)

        for date, matches in user_bets.items():
            print(f"\nProcessing bets for date: {date}")
            for match_id, bet in matches.items():
                print(f"Match: {match_id}, Bet: {bet}")
                actual_result = self.get_actual_result(match_id, date, predictions_method)
                print(f"Actual result: {actual_result}")
                if actual_result is not None:
                    if predictions_method == "match_score":
                        points = self.calculate_points_match_score(bet, actual_result, point_scale)
                    elif awarding_points_method == "point_scale":
                        points = self.calculate_points_scale(bet, actual_result, point_scale)
                    elif awarding_points_method == "bookmaker_quotes":
                        points = self.calculate_points_bookmaker(bet, actual_result, match_id, date)
                    total_points += points
                    print(f"Points awarded: {points}")

        print(f"Total points: {total_points}")

        # Save the calculated points to the database
        with self.app.db_connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO user_competitions (user_id, competition_id, points)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, competition_id) 
            DO UPDATE SET points = EXCLUDED.points
            """, (self.app.current_user['email'], self.competition_id, total_points))
        self.app.db_connection.commit()

        print(f"Points saved for competition {self.competition_id}: {total_points}")

    def calculate_points_scale(self, bet, actual_result, point_scale):
        print(f"Calculating points: bet={bet}, actual_result={actual_result}")
        if bet == actual_result:
            if bet.endswith('_extra'):
                print(f"Correct bet in extra time. Points awarded: {point_scale['winner_ot']}")
                return point_scale['winner_ot']
            else:
                print(f"Correct bet in regular time. Points awarded: {point_scale['winner']}")
                return point_scale['winner']
        elif bet.endswith('_extra') and actual_result.endswith('_extra'):
            print(f"Incorrect bet, but both in extra time. Points awarded: {point_scale['loser_ot']}")
            return point_scale['loser_ot']
        else:
            print(f"Incorrect bet. Points awarded: {point_scale['loser']}")
            return point_scale['loser']

    def calculate_points_bookmaker(self, bet, actual_result, match_id, date):
        print(f"Calculating points for bet: {bet}, actual result: {actual_result}")
        if bet.replace('_extra', '') == actual_result.replace('_extra', ''):
            # Convert date to DD/MM/YYYY format if it's in YYYY-MM-DD format
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
            except ValueError:
                formatted_date = date  # Assume it's already in DD/MM/YYYY format

            if self.app.quotes.exists(formatted_date):
                date_quotes = self.app.quotes[formatted_date]
                match_quotes = date_quotes.get(match_id, {})

                if not match_quotes:
                    print(f"No quotes found for match {match_id} on {formatted_date}")
                    return 0

                # Use the actual_result to look up the odds, not the bet
                odds = match_quotes.get(actual_result, match_quotes.get(actual_result.replace('_extra', ''), 1.0))
                points = int(odds * 100)
                print(f"Odds: {odds}, Points awarded: {points}")
                return points
            else:
                print(f"No quotes found for date {formatted_date}")
                return 0
        print("Bet does not match actual result, no points awarded")
        return 0

    def calculate_points_match_score(self, bet, actual_result, point_scale):
        print(f"Calculating points: bet={bet}, actual_result={actual_result}")

        # Handle string bets
        if isinstance(bet, str):
            if bet.endswith('_extra'):
                bet = {'score': '0-0', 'winner': bet}
            else:
                bet = {'score': '1-0', 'winner': bet}

        bet_score = bet['score'].split('-')
        actual_score = actual_result['score'].split('-')

        bet_team1_score = int(bet_score[0])
        bet_team2_score = int(bet_score[1])
        actual_team1_score = int(actual_score[0])
        actual_team2_score = int(actual_score[1])

        bet_winner = bet['winner'].lower()
        actual_winner = actual_result['winner'].lower()

        points = 0
        is_extra_time = '_extra' in actual_winner

        # Check for exact score
        if bet_team1_score == actual_team1_score and bet_team2_score == actual_team2_score:
            if is_extra_time:
                points += point_scale.get('exact_score_extra', 3)
                print(f"Exact score in extra time. Points awarded: {points}")
            else:
                points += point_scale.get('exact_score_regular', 4)
                print(f"Exact score in regular time. Points awarded: {points}")

            # Add points for correct winner prediction
            if is_extra_time and bet_winner.endswith('_extra'):
                points += point_scale.get('winner_extra', 1)
                print(f"Correct extra time winner. Points awarded: {points}")
            elif not is_extra_time:
                points += point_scale.get('winner_regular', 2)
                print(f"Correct regular time winner. Points awarded: {points}")

            # Add point for correct goal difference (always true for exact score)
            points += point_scale.get('good_goal_difference', 1)
            print(f"Correct goal difference. Points awarded: {points}")

            print(f"Total points awarded: {points}")
            return points

        # Adjust scores for extra time if not exact match
        if is_extra_time:
            if actual_team1_score > actual_team2_score:
                actual_team1_score -= 1
            else:
                actual_team2_score -= 1

        # Check for correct goal difference
        bet_diff = bet_team1_score - bet_team2_score
        actual_diff = actual_team1_score - actual_team2_score
        if bet_diff == actual_diff:
            points += point_scale.get('good_goal_difference', 1)
            print(f"Correct goal difference. Points awarded: {points}")

        # Check for correct winner
        if is_extra_time:
            if bet_winner.endswith('_extra'):
                if (bet_winner == 'team1_extra' and actual_winner.startswith(
                        actual_result['match'].split(' - ')[0].lower())) or \
                        (bet_winner == 'team2_extra' and actual_winner.startswith(
                            actual_result['match'].split(' - ')[1].lower())):
                    points += point_scale.get('winner_extra', 1)
                    print(f"Correct extra time winner. Points awarded: {points}")
        else:
            if bet_winner == actual_winner or (bet_winner.startswith('team') and
                                               ((bet_winner == 'team1' and actual_winner ==
                                                 actual_result['match'].split(' - ')[0].lower()) or
                                                (bet_winner == 'team2' and actual_winner ==
                                                 actual_result['match'].split(' - ')[1].lower()))):
                points += point_scale.get('winner_regular', 2)
                print(f"Correct regular time winner. Points awarded: {points}")

        if points > 0:
            print(f"Total points awarded: {points}")
        else:
            print("Incorrect bet. Points awarded: 0")

        return points

    def get_actual_result(self, match_id, date, predictions_method):
        app = MDApp.get_running_app()

        # Ensure the CSV data is loaded
        if app.matches_df_ligue_magnus is None:
            app.load_csv_data_ligue_magnus()

        # Convert date string to datetime object, handling both formats
        try:
            match_date = datetime.strptime(date, '%d/%m/%Y').date()
        except ValueError:
            try:
                match_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                print(f"Error: Invalid date format: {date}")
                return None

        # Find the match in the DataFrame
        match_row = app.matches_df_ligue_magnus[
            (app.matches_df_ligue_magnus['match'] == match_id) &
            (app.matches_df_ligue_magnus['date'].dt.date == match_date)
            ]

        print(f"Searching for match: {match_id} on {match_date}")
        print(f"Found match data: {match_row.to_dict('records')}")

        if match_row.empty:
            print(f"Match {match_id} on {match_date} not found in CSV")
            return None

        # Check if the match is available (has a result)
        if match_row['available'].iloc[0] == 'yes':
            print(f"Match {match_id} on {match_date} has not been played yet")
            return None

        winner = match_row['winner'].iloc[0]
        win_type = match_row['win_type'].iloc[0]
        score = match_row['score'].iloc[0]

        if predictions_method == "match_score":
            result = {
                'score': score,
                'winner': f"{winner.lower()}_extra" if win_type == 'Extra Time' else winner.lower(),
                'match': match_id
            }
        else:  # winner_loser prediction method
            team1, team2 = match_id.split(' - ')
            if winner == team1:
                result = 'team1_extra' if win_type == 'Extra Time' else 'team1'
            else:
                result = 'team2_extra' if win_type == 'Extra Time' else 'team2'

        print(f"Actual result: {result}")
        return result

    def update_user_points(self):
        total_points = self.calculate_points()
        user_email = self.app.current_user['email']
        if 'points' not in self.app.current_user:
            self.app.current_user['points'] = {}
        self.app.current_user['points'][self.competition_id] = total_points
        self.app.users.put(user_email, **self.app.current_user)
        print(f"Updated points for user {user_email}: {total_points}")

    def load_rankings(self):
        # print("Starting load_rankings method")
        competition_data = self.app.load_competition(self.competition_id)
        if competition_data and "rankings_data" in competition_data:
            rankings_data = competition_data["rankings_data"]
            # print("Screen manager screens:", self.ids.screen_manager.screen_names)
            league_rankings_screen = self.ids.screen_manager.get_screen('league_rankings')
            # print("League rankings screen:", league_rankings_screen)
            if hasattr(league_rankings_screen, 'ids'):
                # print("League rankings screen ids:", league_rankings_screen.ids.keys())
                if 'rankings_content' in league_rankings_screen.ids:
                    rankings_content = league_rankings_screen.ids.rankings_content
                    rankings_content.clear_widgets()  # Clear existing widgets

            for row in rankings_data:
                rankings_content.add_widget(
                    MDLabel(text=str(row['rank']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                team_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, size_hint_x=1.8, height=dp(30))

                # Add team icon
                team_icon = MDIconButton(icon=self.app.team_icons.get(row['team'], "hockey-puck"), size_hint_x=0.2)
                team_box.add_widget(team_icon)

                # Add team name
                team_name = MDLabel(text=row['team'], size_hint_x=1.6)
                team_box.add_widget(team_name)

                rankings_content.add_widget(team_box)

                rankings_content.add_widget(
                    MDLabel(text=str(row['points']), size_hint_y=None, size_hint_x=0.8, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['games_played']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['wins']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['overtime_wins']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['overtime_losses']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['losses']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['goals_for']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['goals_against']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['penalty_minutes']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))

            self.rankings_loaded = True

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        # print(f"Switching to: {item_text} in {self.competition_name}")
        # Map translated text to screen names
        screen_map = {
            self.pronostics_text: 'pronostics',
            self.rankings_text: 'rankings',
            self.league_rankings_text: 'league_rankings'
        }
        screen_name = screen_map.get(item_text)
        if screen_name in self.ids.screen_manager.screen_names:
            self.ids.screen_manager.current = screen_name
        else:
            print(f"Screen '{item_text}' not found in {self.competition_name}.")

########
## NL ##
########

class CompetitionScreenNL(MDScreen):
    competition_name = StringProperty("")
    competition_id = StringProperty("")
    unsaved_bets_count = NumericProperty(0)
    pronostics_text = StringProperty()
    rankings_text = StringProperty()
    league_rankings_text = StringProperty()
    no_matches_available_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.competition_name = kwargs.get('competition_name', '')
        self.competition_id = kwargs.get('competition_id', '')
        self.app = MDApp.get_running_app()
        self.rankings_loaded = False
        self.user_bets = {}
        self.unsaved_bets = set()
        # print(f"CompetitionScreenNL initialized with competition_id: {self.competition_id}")

        # Load rankings data once
        self.load_rankings()
        # Load matches data once
        self.load_matches()
        # Translations
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.pronostics_text = app.get_translation("Pronostics")
        self.rankings_text = app.get_translation("Rankings")
        self.league_rankings_text = app.get_translation("League Rankings")
        self.no_matches_available_text = app.get_translation(
            "No matches available yet. Check back later when the playoffs begin.")

    def on_enter(self):
        super().on_enter()
        self.calculate_and_save_points()
        self.update_classement()

    def update_classement(self):
        classement_screen = self.ids.screen_manager.get_screen('rankings')
        if not hasattr(classement_screen.ids, 'classement_content'):
            print("Error: classement_content not found in Classement screen")
            return

        classement_content = classement_screen.ids.classement_content
        classement_content.clear_widgets()

        try:
            with self.app.db_connection.cursor() as cursor:
                cursor.execute("""
                SELECT u.pseudo, uc.points, u.icon
                FROM user_competitions uc
                JOIN users u ON uc.user_id = u.user_id
                WHERE uc.competition_id = %s
                ORDER BY uc.points DESC
                """, (self.competition_id,))
                user_points = cursor.fetchall()
                print(f"user_points: {user_points}")

            if not user_points:
                classement_content.add_widget(MDLabel(text="No users in this competition yet.", size_hint_x=1))
                return

            for rank, user_data in enumerate(user_points, start=1):
                pseudo = user_data['pseudo']
                points = user_data['points']
                icon = user_data['icon']

                row_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", spacing="10dp")
                row_layout.add_widget(MDLabel(text=str(rank), size_hint_x=0.5))
                user_box = MDBoxLayout(orientation="horizontal", size_hint_x=1.8,
                                       pos_hint={"center_x": 0.5, "top": 0.95})
                user_box.add_widget(MDIconButton(icon=icon if icon else "account", size_hint_x=0.2,
                                                 pos_hint={"center_x": 0.5, "top": 1}))
                user_box.add_widget(MDLabel(text=pseudo or "Unknown", valign="center"))
                row_layout.add_widget(user_box)
                row_layout.add_widget(MDLabel(text=str(points), size_hint_x=0.8))
                classement_content.add_widget(row_layout)

        except Exception as e:
            print(f"Error updating classement: {e}")
            classement_content.add_widget(MDLabel(text="Error loading ranking. Please try again later.", size_hint_x=1))

    def load_matches(self):
        app = MDApp.get_running_app()
        quotes_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/quotes_NL.csv"
        quotes_response = requests.get(quotes_url)
        if quotes_response.status_code == 200:
            quotes_data = {}
            csv_content = StringIO(quotes_response.text)
            csv_reader = csv.DictReader(csv_content)
            for row in csv_reader:
                date = row['date']
                match = row['match']
                if date not in quotes_data:
                    quotes_data[date] = {}
                quotes_data[date][match] = {
                    'team1': float(row['team1']),
                    'team2': float(row['team2']),
                    'draw': float(row['draw']),
                    'team1_extra': float(row['team1_extra']),
                    'team2_extra': float(row['team2_extra'])
                }
        else:
            quotes_data = {}

        competition_data = self.app.load_competition(self.competition_id)
        if competition_data and "upcoming_matches" in competition_data:
            upcoming_matches = competition_data["upcoming_matches"]
            user_bets = self.app.load_user_bets(self.app.current_user['email'], self.competition_id)
            predictions_method = competition_data.get("predictions_method", "winner_loser")
            awarding_points_method = competition_data.get("awarding_points_method", "point_scale")

            rules = competition_data.get('rules', {})
            if isinstance(rules, str):
                rules = json.loads(rules)
            point_scale = rules.get('point_scale', {})

            default_point_scale = {
                'winner': 3,
                'winner_ot': 2,
                'loser_ot': 1,
                'loser': 0
            }
            for key, value in default_point_scale.items():
                if key not in point_scale:
                    point_scale[key] = value

            pronostics_screen = self.ids.screen_manager.get_screen('pronostics')
            matches_layout = pronostics_screen.ids.matches_layout
            matches_layout.clear_widgets()

            if not upcoming_matches:
                no_matches_label = MDLabel(
                    text=app.get_translation("No matches available yet. Check back later when the playoffs begin."),
                    halign="center",
                    adaptive_size=True,
                    theme_text_color="Secondary"
                )
                matches_layout.add_widget(no_matches_label)
            else:
                for match in upcoming_matches:
                    if predictions_method == "winner_loser":
                        match_widget = MatchWidgetWinnerLoser()
                    else:
                        match_widget = MatchWidgetMatchScore()

                    match_date = pd.to_datetime(match['date']).date()
                    match_widget.date = match_date.strftime('%d/%m/%Y')
                    comparison_date = match_date.strftime('%Y-%m-%d')
                    # match_widget.journee = f"Journée {match['journee']}"
                    team1, team2 = match['match'].split(' - ')
                    match_widget.team1 = team1
                    match_widget.team2 = team2
                    match_widget.team1_icon = self.app.team_icons.get(team1, "hockey-puck")
                    match_widget.team2_icon = self.app.team_icons.get(team2, "hockey-puck")

                    if awarding_points_method == "bookmaker_quotes":
                        formatted_date = match_date.strftime('%Y-%m-%d')
                        match_id = f"{team1} - {team2}"

                        if formatted_date in quotes_data and match_id in quotes_data[formatted_date]:
                            quotes = quotes_data[formatted_date][match_id]
                        else:
                            quotes = {
                                'team1': 2.0,
                                'team2': 2.0,
                                'draw': 3.0,
                                'team1_extra': 4.0,
                                'team2_extra': 4.0
                            }

                        match_widget.team1_odds = str(quotes['team1'])
                        match_widget.team2_odds = str(quotes['team2'])
                        match_widget.draw_odds = str(quotes['draw'])
                        match_widget.team1_extra_odds = str(quotes['team1_extra'])
                        match_widget.team2_extra_odds = str(quotes['team2_extra'])
                        match_widget.show_odds = True

                    elif awarding_points_method == "point_scale":
                        match_widget.winner_points = point_scale['winner']
                        match_widget.winner_ot_points = point_scale['winner_ot']
                        match_widget.loser_ot_points = point_scale['loser_ot']
                        match_widget.loser_points = point_scale['loser']
                        match_widget.show_odds = False

                    match_id = f"{match_widget.team1} - {match_widget.team2}"

                    if comparison_date in user_bets and match_id in user_bets[comparison_date]:
                        match_widget.select_outcome(user_bets[comparison_date][match_id])

                    match_widget.bind(selected_outcome=lambda instance, value: self.on_bet_placed(instance))
                    matches_layout.add_widget(match_widget)

                    if comparison_date not in user_bets or match_id not in user_bets[comparison_date]:
                        self.add_unsaved_bet(match_id)
                    match_widget.bind(selected_outcome=lambda instance, value: self.on_bet_placed(instance))
                    self.count_unsaved_bets()

    def count_unsaved_bets(self):
        self.unsaved_bets_count = len(self.unsaved_bets)

    def on_bet_placed(self, match_widget):
        match_id = f"{match_widget.team1} - {match_widget.team2}"
        date = match_widget.date
        bet = match_widget.selected_outcome

        # Ensure the date is in the correct format (DD/MM/YYYY)
        try:
            formatted_date = datetime.strptime(date, '%d/%m/%Y').strftime('%d/%m/%Y')
        except ValueError:
            print(f"Error: Invalid date format: {date}")
            return

        self.app.save_user_bets(
            self.app.current_user['email'],
            self.competition_id,
            formatted_date,
            {match_id: bet}
        )

        # Remove the saved bet from unsaved_bets
        self.unsaved_bets.discard(match_id)
        self.count_unsaved_bets()

    def add_unsaved_bet(self, match_id):
        self.unsaved_bets.add(match_id)
        self.count_unsaved_bets()

    def calculate_and_save_points(self):
        competition_data = self.app.load_competition(self.competition_id)
        predictions_method = competition_data.get("predictions_method", "winner_loser")
        awarding_points_method = competition_data.get("awarding_points_method", "point_scale")

        if predictions_method == "match_score":
            point_scale = competition_data.get("point_scale", {
                "good_goal_difference": 1,
                "exact_score_regular": 4,
                "exact_score_extra": 3,
                "winner_regular": 2,
                "winner_extra": 1,
                "loser_regular": 0,
                "loser_extra": 0
            })
        else:
            point_scale = competition_data.get("point_scale", {
                'winner': 3,
                'winner_ot': 2,
                'loser_ot': 1,
                'loser': 0
            })

        print(f"Calculating points for competition {self.competition_id}")
        print(f"Predictions method: {predictions_method}")
        print(f"Awarding points method: {awarding_points_method}")

        total_points = 0
        user_bets = self.app.load_user_bets(self.app.current_user['email'], self.competition_id)

        for date, matches in user_bets.items():
            print(f"\nProcessing bets for date: {date}")
            for match_id, bet in matches.items():
                print(f"Match: {match_id}, Bet: {bet}")
                actual_result = self.get_actual_result(match_id, date, predictions_method)
                print(f"Actual result: {actual_result}")
                if actual_result is not None:
                    if predictions_method == "match_score":
                        points = self.calculate_points_match_score(bet, actual_result, point_scale)
                    elif awarding_points_method == "point_scale":
                        points = self.calculate_points_scale(bet, actual_result, point_scale)
                    elif awarding_points_method == "bookmaker_quotes":
                        points = self.calculate_points_bookmaker(bet, actual_result, match_id, date)
                    total_points += points
                    print(f"Points awarded: {points}")

        print(f"Total points: {total_points}")

        # Save the calculated points to the database
        with self.app.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_competitions (user_id, competition_id, points)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, competition_id) 
                DO UPDATE SET points = EXCLUDED.points
                """, (self.app.current_user['email'], self.competition_id, total_points))
        self.app.db_connection.commit()

        print(f"Points saved for competition {self.competition_id}: {total_points}")

    def calculate_points_scale(self, bet, actual_result, point_scale):
        print(f"Calculating points: bet={bet}, actual_result={actual_result}")
        if bet == actual_result:
            if bet.endswith('_extra'):
                print(f"Correct bet in extra time. Points awarded: {point_scale['winner_ot']}")
                return point_scale['winner_ot']
            else:
                print(f"Correct bet in regular time. Points awarded: {point_scale['winner']}")
                return point_scale['winner']
        elif bet.endswith('_extra') and actual_result.endswith('_extra'):
            print(f"Incorrect bet, but both in extra time. Points awarded: {point_scale['loser_ot']}")
            return point_scale['loser_ot']
        else:
            print(f"Incorrect bet. Points awarded: {point_scale['loser']}")
            return point_scale['loser']

    def calculate_points_bookmaker(self, bet, actual_result, match_id, date):
        print(f"Calculating points for bet: {bet}, actual result: {actual_result}")
        if bet.replace('_extra', '') == actual_result.replace('_extra', ''):
            # Convert date to DD/MM/YYYY format if it's in YYYY-MM-DD format
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
            except ValueError:
                formatted_date = date  # Assume it's already in DD/MM/YYYY format

            if self.app.quotes.exists(formatted_date):
                date_quotes = self.app.quotes[formatted_date]
                match_quotes = date_quotes.get(match_id, {})

                if not match_quotes:
                    print(f"No quotes found for match {match_id} on {formatted_date}")
                    return 0

                # Use the actual_result to look up the odds, not the bet
                odds = match_quotes.get(actual_result, match_quotes.get(actual_result.replace('_extra', ''), 1.0))
                points = int(odds * 100)
                print(f"Odds: {odds}, Points awarded: {points}")
                return points
            else:
                print(f"No quotes found for date {formatted_date}")
                return 0
        print("Bet does not match actual result, no points awarded")
        return 0

    def calculate_points_match_score(self, bet, actual_result, point_scale):
        print(f"Calculating points: bet={bet}, actual_result={actual_result}")

        # Handle string bets
        if isinstance(bet, str):
            if bet.endswith('_extra'):
                bet = {'score': '0-0', 'winner': bet}
            else:
                bet = {'score': '1-0', 'winner': bet}

        bet_score = bet['score'].split('-')
        actual_score = actual_result['score'].split('-')

        bet_team1_score = int(bet_score[0])
        bet_team2_score = int(bet_score[1])
        actual_team1_score = int(actual_score[0])
        actual_team2_score = int(actual_score[1])

        bet_winner = bet['winner'].lower()
        actual_winner = actual_result['winner'].lower()

        points = 0
        is_extra_time = '_extra' in actual_winner

        # Check for exact score
        if bet_team1_score == actual_team1_score and bet_team2_score == actual_team2_score:
            if is_extra_time:
                points += point_scale.get('exact_score_extra', 3)
                print(f"Exact score in extra time. Points awarded: {points}")
            else:
                points += point_scale.get('exact_score_regular', 4)
                print(f"Exact score in regular time. Points awarded: {points}")

            # Add points for correct winner prediction
            if is_extra_time and bet_winner.endswith('_extra'):
                points += point_scale.get('winner_extra', 1)
                print(f"Correct extra time winner. Points awarded: {points}")
            elif not is_extra_time:
                points += point_scale.get('winner_regular', 2)
                print(f"Correct regular time winner. Points awarded: {points}")

            # Add point for correct goal difference (always true for exact score)
            points += point_scale.get('good_goal_difference', 1)
            print(f"Correct goal difference. Points awarded: {points}")

            print(f"Total points awarded: {points}")
            return points

        # Adjust scores for extra time if not exact match
        if is_extra_time:
            if actual_team1_score > actual_team2_score:
                actual_team1_score -= 1
            else:
                actual_team2_score -= 1

        # Check for correct goal difference
        bet_diff = bet_team1_score - bet_team2_score
        actual_diff = actual_team1_score - actual_team2_score
        if bet_diff == actual_diff:
            points += point_scale.get('good_goal_difference', 1)
            print(f"Correct goal difference. Points awarded: {points}")

        # Check for correct winner
        if is_extra_time:
            if bet_winner.endswith('_extra'):
                if (bet_winner == 'team1_extra' and actual_winner.startswith(
                        actual_result['match'].split(' - ')[0].lower())) or \
                        (bet_winner == 'team2_extra' and actual_winner.startswith(
                            actual_result['match'].split(' - ')[1].lower())):
                    points += point_scale.get('winner_extra', 1)
                    print(f"Correct extra time winner. Points awarded: {points}")
        else:
            if bet_winner == actual_winner or (bet_winner.startswith('team') and
                                               ((bet_winner == 'team1' and actual_winner ==
                                                 actual_result['match'].split(' - ')[0].lower()) or
                                                (bet_winner == 'team2' and actual_winner ==
                                                 actual_result['match'].split(' - ')[1].lower()))):
                points += point_scale.get('winner_regular', 2)
                print(f"Correct regular time winner. Points awarded: {points}")

        if points > 0:
            print(f"Total points awarded: {points}")
        else:
            print("Incorrect bet. Points awarded: 0")

        return points

    def get_actual_result(self, match_id, date, predictions_method):
        app = MDApp.get_running_app()

        # Ensure the CSV data is loaded
        if app.matches_df_nl is None:
            app.load_csv_data_nl()

        # Convert date string to datetime object, handling both formats
        try:
            match_date = datetime.strptime(date, '%d/%m/%Y').date()
        except ValueError:
            try:
                match_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                print(f"Error: Invalid date format: {date}")
                return None

        # Find the match in the DataFrame
        match_row = app.matches_df_ligue_magnus[
            (app.matches_df_ligue_magnus['match'] == match_id) &
            (app.matches_df_ligue_magnus['date'].dt.date == match_date)
            ]

        print(f"Searching for match: {match_id} on {match_date}")
        print(f"Found match data: {match_row.to_dict('records')}")

        if match_row.empty:
            print(f"Match {match_id} on {match_date} not found in CSV")
            return None

        # Check if the match is available (has a result)
        if match_row['available'].iloc[0] == 'yes':
            print(f"Match {match_id} on {match_date} has not been played yet")
            return None

        winner = match_row['winner'].iloc[0]
        win_type = match_row['win_type'].iloc[0]
        score = match_row['score'].iloc[0]

        if predictions_method == "match_score":
            result = {
                'score': score,
                'winner': f"{winner.lower()}_extra" if win_type == 'Extra Time' else winner.lower(),
                'match': match_id
            }
        else:  # winner_loser prediction method
            team1, team2 = match_id.split(' - ')
            if winner == team1:
                result = 'team1_extra' if win_type == 'Extra Time' else 'team1'
            else:
                result = 'team2_extra' if win_type == 'Extra Time' else 'team2'

        print(f"Actual result: {result}")
        return result

    def update_user_points(self):
        total_points = self.calculate_points()
        user_email = self.app.current_user['email']
        if 'points' not in self.app.current_user:
            self.app.current_user['points'] = {}
        self.app.current_user['points'][self.competition_id] = total_points
        self.app.users.put(user_email, **self.app.current_user)
        print(f"Updated points for user {user_email}: {total_points}")

    def load_rankings(self):
        print("Starting load_rankings method")
        competition_data = self.app.load_competition(self.competition_id)
        if competition_data and "rankings_data" in competition_data:
            rankings_data = competition_data["rankings_data"]
            print("Screen manager screens:", self.ids.screen_manager.screen_names)
            league_rankings_screen = self.ids.screen_manager.get_screen('league_rankings')
            print("League rankings screen:", league_rankings_screen)
            if hasattr(league_rankings_screen, 'ids'):
                print("League rankings screen ids:", league_rankings_screen.ids.keys())
                if 'rankings_content' in league_rankings_screen.ids:
                    rankings_content = league_rankings_screen.ids.rankings_content
                    rankings_content.clear_widgets()  # Clear existing widgets

            for row in rankings_data:
                rankings_content.add_widget(
                    MDLabel(text=str(row['rank']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                # Create a box layout for team name and icon
                team_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, size_hint_x=1.8, height=dp(30))

                # Add team icon
                team_icon = MDIconButton(icon=self.app.team_icons.get(row['team'], "hockey-puck"), size_hint_x=0.2)
                team_box.add_widget(team_icon)

                # Add team name
                team_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, size_hint_x=1.8, height=dp(30))

                # Add team icon
                team_icon = MDIconButton(icon=self.app.team_icons.get(row['team'], "hockey-puck"), size_hint_x=0.2)
                team_box.add_widget(team_icon)

                # Add team name
                team_name = MDLabel(text=row['team'], size_hint_x=1.6)
                team_box.add_widget(team_name)

                rankings_content.add_widget(team_box)

                rankings_content.add_widget(
                    MDLabel(text=str(row['points']), size_hint_y=None, size_hint_x=0.8, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['games_played']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['wins']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['overtime_wins']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['overtime_losses']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['losses']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['goals_for']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['goals_against']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))

            self.rankings_loaded = True

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        # print(f"Switching to: {item_text} in {self.competition_name}")
        # Map translated text to screen names
        screen_map = {
            self.pronostics_text: 'pronostics',
            self.rankings_text: 'rankings',
            self.league_rankings_text: 'league_rankings'
        }
        screen_name = screen_map.get(item_text)
        if screen_name in self.ids.screen_manager.screen_names:
            self.ids.screen_manager.current = screen_name
        else:
            print(f"Screen '{item_text}' not found in {self.competition_name}.")

class CompetitionScreenFourNations(MDScreen):
    competition_name = StringProperty("")
    competition_id = StringProperty("")
    unsaved_bets_count = NumericProperty(0)
    pronostics_text = StringProperty()
    rankings_text = StringProperty()
    league_rankings_text = StringProperty()
    canada_text = StringProperty()
    sweden_text = StringProperty()
    finland_text = StringProperty()
    usa_text = StringProperty()
    no_matches_available_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.competition_name = kwargs.get('competition_name', '')
        self.competition_id = kwargs.get('competition_id', '')
        self.app = MDApp.get_running_app()
        self.rankings_loaded = False
        self.user_bets = {}
        self.unsaved_bets = set()
        self.team_translations = {}  # Initialize team_translations here

        # Load rankings data once
        self.load_rankings()
        # Translations
        self.update_translations()
        # Load matches data once
        self.load_matches()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.pronostics_text = app.get_translation("Pronostics")
        self.rankings_text = app.get_translation("Rankings")
        self.league_rankings_text = app.get_translation("League Rankings")
        self.canada_text = app.get_translation("Canada")
        self.sweden_text = app.get_translation("Sweden")
        self.finland_text = app.get_translation("Finland")
        self.usa_text = app.get_translation("USA")
        self.no_matches_available_text = app.get_translation(
            "No matches available yet. Check back later when the playoffs begin.")

        # Update team translations
        self.team_translations = {
            "Sweden": app.get_translation("Sweden"),
            "USA": app.get_translation("USA"),
            "Finland": app.get_translation("Finland"),
            "Canada": app.get_translation("Canada")
        }
        print(f"Updated team translations: {self.team_translations}")

    def translate_team_name(self, team_name):
        return self.team_translations.get(team_name, team_name)

    def on_enter(self):
        super().on_enter()
        self.calculate_and_save_points()
        self.update_classement()

    def update_classement(self):
        classement_screen = self.ids.screen_manager.get_screen('rankings')
        if not hasattr(classement_screen.ids, 'classement_content'):
            print("Error: classement_content not found in Classement screen")
            return

        classement_content = classement_screen.ids.classement_content
        classement_content.clear_widgets()

        try:
            with self.app.db_connection.cursor() as cursor:
                cursor.execute("""
                SELECT u.pseudo, uc.points, u.icon
                FROM user_competitions uc
                JOIN users u ON uc.user_id = u.user_id
                WHERE uc.competition_id = %s
                ORDER BY uc.points DESC
                """, (self.competition_id,))
                user_points = cursor.fetchall()
                print(f"user_points: {user_points}")

            if not user_points:
                classement_content.add_widget(MDLabel(text="No users in this competition yet.", size_hint_x=1))
                return

            for rank, user_data in enumerate(user_points, start=1):
                pseudo = user_data['pseudo']
                points = user_data['points']
                icon = user_data['icon']

                row_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", spacing="10dp")
                row_layout.add_widget(MDLabel(text=str(rank), size_hint_x=0.5))
                user_box = MDBoxLayout(orientation="horizontal", size_hint_x=1.8,
                                       pos_hint={"center_x": 0.5, "top": 0.95})
                user_box.add_widget(MDIconButton(icon=icon if icon else "account", size_hint_x=0.2,
                                                 pos_hint={"center_x": 0.5, "top": 1}))
                user_box.add_widget(MDLabel(text=pseudo or "Unknown", valign="center"))
                row_layout.add_widget(user_box)
                row_layout.add_widget(MDLabel(text=str(points), size_hint_x=0.8))
                classement_content.add_widget(row_layout)

        except Exception as e:
            print(f"Error updating classement: {e}")
            classement_content.add_widget(MDLabel(text="Error loading ranking. Please try again later.", size_hint_x=1))

    def load_matches(self):
        app = MDApp.get_running_app()
        quotes_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/quotes_fournations.json"
        quotes_response = requests.get(quotes_url)
        if quotes_response.status_code == 200:
            quotes_data = quotes_response.json()
        else:
            quotes_data = {}
        competition_data = self.app.load_competition(self.competition_id)
        if competition_data and "upcoming_matches" in competition_data:
            upcoming_matches = competition_data["upcoming_matches"]
            user_bets = self.app.load_user_bets(self.app.current_user['email'], self.competition_id)
            predictions_method = competition_data.get("predictions_method", "winner_loser")
            awarding_points_method = competition_data.get("awarding_points_method", "point_scale")

            rules = competition_data.get('rules', {})
            if isinstance(rules, str):
                rules = json.loads(rules)
            point_scale = rules.get('point_scale', {})

            default_point_scale = {
                'winner': 3,
                'winner_ot': 2,
                'loser_ot': 1,
                'loser': 0
            }
            for key, value in default_point_scale.items():
                if key not in point_scale:
                    point_scale[key] = value

            pronostics_screen = self.ids.screen_manager.get_screen('pronostics')
            matches_layout = pronostics_screen.ids.matches_layout
            matches_layout.clear_widgets()

            if not upcoming_matches:
                no_matches_label = MDLabel(
                    text=app.get_translation("No matches available yet. Check back later when the playoffs begin."),
                    halign="center",
                    adaptive_size=True,
                    theme_text_color="Secondary"
                )
                matches_layout.add_widget(no_matches_label)
            else:
                for match in upcoming_matches:
                    if predictions_method == "winner_loser":
                        match_widget = MatchWidgetWinnerLoser()
                    else:
                        match_widget = MatchWidgetMatchScore()

                    match_date = pd.to_datetime(match['date']).date()
                    match_widget.date = match_date.strftime('%d/%m/%Y')
                    comparison_date = match_date.strftime('%Y-%m-%d')
                    # match_widget.journee = f"Journée {match['journee']}"
                    team1, team2 = match['match'].split(' - ')
                    translated_team1 = self.translate_team_name(team1)
                    translated_team2 = self.translate_team_name(team2)
                    match_widget.team1 = translated_team1
                    match_widget.team2 = translated_team2
                    match_widget.team1_icon = self.app.team_icons.get(team1, "hockey-puck")
                    match_widget.team2_icon = self.app.team_icons.get(team2, "hockey-puck")

                    if awarding_points_method == "bookmaker_quotes":
                        formatted_date = match_date.strftime('%Y-%m-%d')
                        match_id = f"{team1} - {team2}"

                        if formatted_date in quotes_data and match_id in quotes_data[formatted_date]:
                            quotes = quotes_data[formatted_date][match_id]
                        else:
                            quotes = {
                                'team1': 2.0,
                                'team2': 2.0,
                                'draw': 3.0,
                                'team1_extra': 4.0,
                                'team2_extra': 4.0
                            }

                        match_widget.team1_odds = str(quotes['team1'])
                        match_widget.team2_odds = str(quotes['team2'])
                        match_widget.draw_odds = str(quotes['draw'])
                        match_widget.team1_extra_odds = str(quotes['team1_extra'])
                        match_widget.team2_extra_odds = str(quotes['team2_extra'])
                        match_widget.show_odds = True

                    elif awarding_points_method == "point_scale":
                        match_widget.winner_points = point_scale['winner']
                        match_widget.winner_ot_points = point_scale['winner_ot']
                        match_widget.loser_ot_points = point_scale['loser_ot']
                        match_widget.loser_points = point_scale['loser']
                        match_widget.show_odds = False

                    # match_id = f"{match_widget.team1} - {match_widget.team2}"
                    #
                    # if comparison_date in user_bets and match_id in user_bets[comparison_date]:
                    #     match_widget.select_outcome(user_bets[comparison_date][match_id])

                    original_match_id = f"{team1} - {team2}"
                    translated_match_id = f"{translated_team1} - {translated_team2}"

                    if comparison_date in user_bets:
                        if original_match_id in user_bets[comparison_date]:
                            match_widget.select_outcome(user_bets[comparison_date][original_match_id])
                        elif translated_match_id in user_bets[comparison_date]:
                            match_widget.select_outcome(user_bets[comparison_date][translated_match_id])

                    match_widget.bind(selected_outcome=lambda instance, value: self.on_bet_placed(instance))
                    matches_layout.add_widget(match_widget)

                    if comparison_date not in user_bets or (
                            original_match_id not in user_bets[comparison_date] and translated_match_id not in
                            user_bets[comparison_date]):
                        self.add_unsaved_bet(original_match_id)

    def count_unsaved_bets(self):
        self.unsaved_bets_count = len(self.unsaved_bets)

    def on_bet_placed(self, match_widget):
        app = MDApp.get_running_app()
        team1_english = self.app.translate_to_english(match_widget.team1)
        team2_english = self.app.translate_to_english(match_widget.team2)
        match_id = f"{team1_english} - {team2_english}"
        date = match_widget.date
        bet = match_widget.selected_outcome

        # Ensure the date is in the correct format (DD/MM/YYYY)
        try:
            formatted_date = datetime.strptime(date, '%d/%m/%Y').strftime('%d/%m/%Y')
        except ValueError:
            print(f"Error: Invalid date format: {date}")
            return

        self.app.save_user_bets(
            self.app.current_user['email'],
            self.competition_id,
            formatted_date,
            {match_id: bet}
        )

        # Remove the saved bet from unsaved_bets
        self.unsaved_bets.discard(match_id)
        self.count_unsaved_bets()

    def add_unsaved_bet(self, match_id):
        app = MDApp.get_running_app()
        team1, team2 = match_id.split(' - ')
        team1_english = self.app.translate_to_english(team1)
        team2_english = self.app.translate_to_english(team2)
        english_match_id = f"{team1_english} - {team2_english}"
        self.unsaved_bets.add(english_match_id)
        self.count_unsaved_bets()

    def calculate_and_save_points(self):
        competition_data = self.app.load_competition(self.competition_id)
        predictions_method = competition_data.get("predictions_method", "winner_loser")
        awarding_points_method = competition_data.get("awarding_points_method", "point_scale")

        if predictions_method == "match_score":
            point_scale = competition_data.get("point_scale", {
                "good_goal_difference": 1,
                "exact_score_regular": 4,
                "exact_score_extra": 3,
                "winner_regular": 2,
                "winner_extra": 1,
                "loser_regular": 0,
                "loser_extra": 0
            })
        else:
            point_scale = competition_data.get("point_scale", {
                'winner': 3,
                'winner_ot': 2,
                'loser_ot': 1,
                'loser': 0
            })

        print(f"Calculating points for competition {self.competition_id}")
        print(f"Predictions method: {predictions_method}")
        print(f"Awarding points method: {awarding_points_method}")

        total_points = 0
        user_bets = self.app.load_user_bets(self.app.current_user['email'], self.competition_id)

        for date, matches in user_bets.items():
            print(f"\nProcessing bets for date: {date}")
            for match_id, bet in matches.items():
                print(f"Match: {match_id}, Bet: {bet}")
                actual_result = self.get_actual_result(match_id, date, predictions_method)
                print(f"Actual result: {actual_result}")
                if actual_result is not None:
                    if predictions_method == "match_score":
                        points = self.calculate_points_match_score(bet, actual_result, point_scale)
                    elif awarding_points_method == "point_scale":
                        points = self.calculate_points_scale(bet, actual_result, point_scale)
                    elif awarding_points_method == "bookmaker_quotes":
                        points = self.calculate_points_bookmaker(bet, actual_result, match_id, date)
                    total_points += points
                    print(f"Points awarded: {points}")

        print(f"Total points: {total_points}")

        # Save the calculated points to the database
        with self.app.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_competitions (user_id, competition_id, points)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, competition_id) 
                DO UPDATE SET points = EXCLUDED.points
                """, (self.app.current_user['email'], self.competition_id, total_points))
        self.app.db_connection.commit()

        print(f"Points saved for competition {self.competition_id}: {total_points}")

    def calculate_points_scale(self, bet, actual_result, point_scale):
        print(f"Calculating points: bet={bet}, actual_result={actual_result}")
        if bet == actual_result:
            if bet.endswith('_extra'):
                print(f"Correct bet in extra time. Points awarded: {point_scale['winner_ot']}")
                return point_scale['winner_ot']
            else:
                print(f"Correct bet in regular time. Points awarded: {point_scale['winner']}")
                return point_scale['winner']
        elif bet.endswith('_extra') and actual_result.endswith('_extra'):
            print(f"Incorrect bet, but both in extra time. Points awarded: {point_scale['loser_ot']}")
            return point_scale['loser_ot']
        else:
            print(f"Incorrect bet. Points awarded: {point_scale['loser']}")
            return point_scale['loser']

    def calculate_points_bookmaker(self, bet, actual_result, match_id, date):
        print(f"Calculating points for bet: {bet}, actual result: {actual_result}")
        if bet.replace('_extra', '') == actual_result.replace('_extra', ''):
            # Convert date to DD/MM/YYYY format if it's in YYYY-MM-DD format
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m/%Y')
            except ValueError:
                formatted_date = date  # Assume it's already in DD/MM/YYYY format

            if self.app.quotes.exists(formatted_date):
                date_quotes = self.app.quotes[formatted_date]
                match_quotes = date_quotes.get(match_id, {})

                if not match_quotes:
                    print(f"No quotes found for match {match_id} on {formatted_date}")
                    return 0

                # Use the actual_result to look up the odds, not the bet
                odds = match_quotes.get(actual_result, match_quotes.get(actual_result.replace('_extra', ''), 1.0))
                points = int(odds * 100)
                print(f"Odds: {odds}, Points awarded: {points}")
                return points
            else:
                print(f"No quotes found for date {formatted_date}")
                return 0
        print("Bet does not match actual result, no points awarded")
        return 0

    def calculate_points_match_score(self, bet, actual_result, point_scale):
        print(f"Calculating points: bet={bet}, actual_result={actual_result}")

        # Handle string bets
        if isinstance(bet, str):
            if bet.endswith('_extra'):
                bet = {'score': '0-0', 'winner': bet}
            else:
                bet = {'score': '1-0', 'winner': bet}

        bet_score = bet['score'].split('-')
        actual_score = actual_result['score'].split('-')

        bet_team1_score = int(bet_score[0])
        bet_team2_score = int(bet_score[1])
        actual_team1_score = int(actual_score[0])
        actual_team2_score = int(actual_score[1])

        bet_winner = bet['winner'].lower()
        actual_winner = actual_result['winner'].lower()

        points = 0
        is_extra_time = '_extra' in actual_winner

        # Check for exact score
        if bet_team1_score == actual_team1_score and bet_team2_score == actual_team2_score:
            if is_extra_time:
                points += point_scale.get('exact_score_extra', 3)
                print(f"Exact score in extra time. Points awarded: {points}")
            else:
                points += point_scale.get('exact_score_regular', 4)
                print(f"Exact score in regular time. Points awarded: {points}")

            # Add points for correct winner prediction
            if is_extra_time and bet_winner.endswith('_extra'):
                points += point_scale.get('winner_extra', 1)
                print(f"Correct extra time winner. Points awarded: {points}")
            elif not is_extra_time:
                points += point_scale.get('winner_regular', 2)
                print(f"Correct regular time winner. Points awarded: {points}")

            # Add point for correct goal difference (always true for exact score)
            points += point_scale.get('good_goal_difference', 1)
            print(f"Correct goal difference. Points awarded: {points}")

            print(f"Total points awarded: {points}")
            return points

        # Adjust scores for extra time if not exact match
        if is_extra_time:
            if actual_team1_score > actual_team2_score:
                actual_team1_score -= 1
            else:
                actual_team2_score -= 1

        # Check for correct goal difference
        bet_diff = bet_team1_score - bet_team2_score
        actual_diff = actual_team1_score - actual_team2_score
        if bet_diff == actual_diff:
            points += point_scale.get('good_goal_difference', 1)
            print(f"Correct goal difference. Points awarded: {points}")

        # Check for correct winner
        if is_extra_time:
            if bet_winner.endswith('_extra'):
                if (bet_winner == 'team1_extra' and actual_winner.startswith(
                        actual_result['match'].split(' - ')[0].lower())) or \
                        (bet_winner == 'team2_extra' and actual_winner.startswith(
                            actual_result['match'].split(' - ')[1].lower())):
                    points += point_scale.get('winner_extra', 1)
                    print(f"Correct extra time winner. Points awarded: {points}")
        else:
            if bet_winner == actual_winner or (bet_winner.startswith('team') and
                                               ((bet_winner == 'team1' and actual_winner ==
                                                 actual_result['match'].split(' - ')[0].lower()) or
                                                (bet_winner == 'team2' and actual_winner ==
                                                 actual_result['match'].split(' - ')[1].lower()))):
                points += point_scale.get('winner_regular', 2)
                print(f"Correct regular time winner. Points awarded: {points}")

        if points > 0:
            print(f"Total points awarded: {points}")
        else:
            print("Incorrect bet. Points awarded: 0")

        return points

    def get_actual_result(self, match_id, date, predictions_method):
        app = MDApp.get_running_app()

        # Ensure the CSV data is loaded
        if app.matches_df_fournations is None:
            app.load_csv_data_fournations()

        # Convert date string to datetime object, handling both formats
        try:
            match_date = datetime.strptime(date, '%d/%m/%Y').date()
        except ValueError:
            try:
                match_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                print(f"Error: Invalid date format: {date}")
                return None

        # Find the match in the DataFrame
        match_row = app.matches_df_ligue_magnus[
            (app.matches_df_ligue_magnus['match'] == match_id) &
            (app.matches_df_ligue_magnus['date'].dt.date == match_date)
            ]

        print(f"Searching for match: {match_id} on {match_date}")
        print(f"Found match data: {match_row.to_dict('records')}")

        if match_row.empty:
            print(f"Match {match_id} on {match_date} not found in CSV")
            return None

        # Check if the match is available (has a result)
        if match_row['available'].iloc[0] == 'yes':
            print(f"Match {match_id} on {match_date} has not been played yet")
            return None

        winner = match_row['winner'].iloc[0]
        win_type = match_row['win_type'].iloc[0]
        score = match_row['score'].iloc[0]

        if predictions_method == "match_score":
            result = {
                'score': score,
                'winner': f"{winner.lower()}_extra" if win_type == 'Extra Time' else winner.lower(),
                'match': match_id
            }
        else:  # winner_loser prediction method
            team1, team2 = match_id.split(' - ')
            if winner == team1:
                result = 'team1_extra' if win_type == 'Extra Time' else 'team1'
            else:
                result = 'team2_extra' if win_type == 'Extra Time' else 'team2'

        print(f"Actual result: {result}")
        return result

    def update_user_points(self):
        total_points = self.calculate_points()
        user_email = self.app.current_user['email']
        if 'points' not in self.app.current_user:
            self.app.current_user['points'] = {}
        self.app.current_user['points'][self.competition_id] = total_points
        self.app.users.put(user_email, **self.app.current_user)
        print(f"Updated points for user {user_email}: {total_points}")

    def load_rankings(self):
        print("Starting load_rankings method")
        competition_data = self.app.load_competition(self.competition_id)
        if competition_data and "rankings_data" in competition_data:
            rankings_data = competition_data["rankings_data"]
            print("Screen manager screens:", self.ids.screen_manager.screen_names)
            league_rankings_screen = self.ids.screen_manager.get_screen('league_rankings')
            print("League rankings screen:", league_rankings_screen)
            if hasattr(league_rankings_screen, 'ids'):
                print("League rankings screen ids:", league_rankings_screen.ids.keys())
                if 'rankings_content' in league_rankings_screen.ids:
                    rankings_content = league_rankings_screen.ids.rankings_content
                    rankings_content.clear_widgets()  # Clear existing widgets

            for row in rankings_data:
                rankings_content.add_widget(
                    MDLabel(text=str(row['rank']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))

                # Create a box layout for team name and icon
                team_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, size_hint_x=1.8, height=dp(30))

                # Add team icon
                team_icon = MDIconButton(icon=self.app.team_icons.get(row['team'], "hockey-puck"), size_hint_x=0.2)
                team_box.add_widget(team_icon)

                # Add translated team name
                translated_team_name = self.translate_team_name(row['team'])
                team_name = MDLabel(text=translated_team_name, size_hint_x=1.6)
                team_box.add_widget(team_name)

                rankings_content.add_widget(team_box)

                rankings_content.add_widget(
                    MDLabel(text=str(row['points']), size_hint_y=None, size_hint_x=0.8, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['games_played']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['wins']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['overtime_wins']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['overtime_losses']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['losses']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['goals_for']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))
                rankings_content.add_widget(
                    MDLabel(text=str(row['goals_against']), size_hint_y=None, size_hint_x=0.5, height=dp(30)))

            self.rankings_loaded = True

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        # print(f"Switching to: {item_text} in {self.competition_name}")
        # Map translated text to screen names
        screen_map = {
            self.pronostics_text: 'pronostics',
            self.rankings_text: 'rankings',
            self.league_rankings_text: 'league_rankings'
        }
        screen_name = screen_map.get(item_text)
        if screen_name in self.ids.screen_manager.screen_names:
            self.ids.screen_manager.current = screen_name
        else:
            print(f"Screen '{item_text}' not found in {self.competition_name}.")


"""
###########################################
####### Manage Competition Screen #########
###########################################
"""
# Panel avec les informations des compétitions
# --------------------------------------------
class ListOfYourCompetitionPanel(MDExpansionPanel):
    your_competitions_text = StringProperty()
    competition_information_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.your_competitions_text = app.get_translation("Your Competitions")
        self.competition_information_text = app.get_translation("Competition Information")

    async def populate_competition_list(self):
        competition_grid = self.ids.competition_grid
        competition_grid.clear_widgets()

        with self.app.db_connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.competition_id, c.name, c.type, c.duration, c.awarding_points_method, c.rules, c.contest_mode, c.admin_id, u.pseudo
                FROM competitions c
                JOIN user_competitions uc ON c.competition_id = uc.competition_id
                JOIN users u ON c.admin_id = u.user_id
                WHERE uc.user_id = %s
            """, (self.app.current_user['email'],))
            competitions = cursor.fetchall()

        for competition in competitions:
            if competition['awarding_points_method'] == 'bookmaker_quotes':
                rules_display = "Bookmaker Quotes"
            else:
                rules_display = str(competition['rules'])

            is_admin = competition['admin_id'] == self.app.current_user['email']

            try:
                card = CompetitionCard(
                    competition_name=competition['name'],
                    competition_type=competition['type'],
                    competition_id=competition['competition_id'],
                    competition_duration=competition['duration'],
                    competition_rules=rules_display,
                    contest_mode=competition['contest_mode'],
                    admin_pseudo=competition['pseudo'],
                    is_admin=is_admin
                )
                competition_grid.add_widget(card)
            except Exception as e:
                print(f"Error creating CompetitionCard: {e}")

        await asynckivy.sleep(0)  # Yield to prevent blocking

    def on_open(self):
        asynckivy.start(self.populate_competition_list())

    def tap_expansion_chevron_list_of_your_competition(
            self, panel: MDExpansionPanel, chevron: TrailingPressedIconButton
    ):
        if not self.is_open:
            self.open()
            chevron.icon = "chevron-down"
        else:
            self.close()
            chevron.icon = "chevron-right"
            self.ids.competition_grid.clear_widgets()

        # Force update of panel layout
        def update_layout(dt):
            self.parent.do_layout()
        Clock.schedule_once(update_layout, 0.2)

# Classe permettant d'écrire les informations de la compétition en question --> CompetitionPanel
# -------------------------------------------------------------------------
class CompetitionCard(MDCard):
    competition_name = StringProperty()
    competition_type = StringProperty()
    competition_id = StringProperty()
    competition_duration = StringProperty()
    competition_rules = StringProperty()
    name_text = StringProperty()
    type_text = StringProperty()
    duration_text = StringProperty()
    id_text = StringProperty()
    rules_text = StringProperty()
    confirm_exit_text = StringProperty()
    cancel_text = StringProperty()
    yes_text = StringProperty()
    are_you_sure_text = StringProperty()
    quit_text = StringProperty()
    share_text = StringProperty()
    contest_mode = StringProperty("")
    status_text = StringProperty()
    is_admin = BooleanProperty(False)
    admin_pseudo = StringProperty("")

    def __init__(self, competition_name, competition_type, competition_id, competition_duration, competition_rules, contest_mode, admin_pseudo, is_admin, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.competition_name = competition_name
        self.competition_type = competition_type
        self.competition_id = competition_id
        self.competition_duration = competition_duration
        self.competition_rules = self.format_rules(competition_rules)
        self.padding = "20dp"
        self.spacing = "20dp"
        self.dialog = None
        self.contest_mode = contest_mode
        self.admin_pseudo = admin_pseudo
        self.is_admin = is_admin
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.name_text = app.get_translation("Name")
        self.type_text = app.get_translation("Type")
        self.duration_text = app.get_translation("Duration")
        self.id_text = app.get_translation("ID")
        self.rules_text = app.get_translation("Rules")
        self.confirm_exit_text = app.get_translation("Confirm Exit")
        self.cancel_text = app.get_translation("Cancel")
        self.yes_text = app.get_translation("Yes")
        self.are_you_sure_text = app.get_translation("Are you sure you want to quit {}?")
        self.quit_text = app.get_translation("Quit")
        self.share_text = app.get_translation("Share")
        self.status_text = app.get_translation("Status")

    def toggle_contest_mode(self, switch):
        if self.is_admin:
            new_mode = "open" if switch.active else "closed"
            # Update the database
            app = MDApp.get_running_app()
            with app.db_connection.cursor() as cursor:
                cursor.execute("""
                       UPDATE competitions
                       SET contest_mode = %s
                       WHERE competition_id = %s
                   """, (new_mode, self.competition_id))
            app.db_connection.commit()
            self.contest_mode = new_mode

    def share_competition(self, instance):
        app = MDApp.get_running_app()
        try:
            Clipboard.copy(self.competition_id)
            MDSnackbar(MDSnackbarText(text=app.get_translation("Competition ID copied to clipboard!"))).open()
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            MDSnackbar(MDSnackbarText(text=app.get_translation("Failed to copy competition ID."))).open()

    def format_rules(self, rules):
        if rules == "Bookmaker Quotes":
            return rules
        try:
            rules_dict = eval(rules)
            point_scale = rules_dict.get('point_scale', {})
            formatted_rules = "\n".join([
                f"loser: {point_scale.get('loser', 0)}",
                f"winner: {point_scale.get('winner', 3)}",
                f"loser_ot: {point_scale.get('loser_ot', 1)}",
                f"winner_ot: {point_scale.get('winner_ot', 2)}"
            ])
            return formatted_rules
        except:
            return "Invalid rules format"

    def show_confirmation_dialog(self):
        app = MDApp.get_running_app()
        if not self.dialog:
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                text=app.get_translation("Confirm Exit")),
                MDDialogSupportingText(
                text=self.are_you_sure_text.format(self.competition_name)
                ),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(
                            text=app.get_translation("Yes")),
                        on_release=self.confirm_remove_competition
                    ),
                    MDButton(
                        MDButtonText(
                            text=app.get_translation("Cancel")),
                        on_release=self.dismiss_dialog
                    ),
                    spacing="350dp"
                )
            )
        self.dialog.open()

    def dismiss_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def confirm_remove_competition(self, *args):
        app = MDApp.get_running_app()
        self.dismiss_dialog()
        self.remove_competition()
        self.app.switch_to_main_screen()
        MDSnackbar(MDSnackbarText(text=app.get_translation("{competition_name} deleted successfully").format(competition_name=self.competition_name))).open()

    def remove_competition(self):
        app = MDApp.get_running_app()
        try:
            with app.db_connection:
                with app.db_connection.cursor() as cursor:
                    print(
                        f"Attempting to remove user {app.current_user['email']} from competition {self.competition_id}")

                    # Check if the user is the admin
                    cursor.execute("""
                    SELECT admin_id FROM competitions
                    WHERE competition_id = %s
                    """, (self.competition_id,))
                    current_admin = cursor.fetchone()['admin_id']

                    is_admin = current_admin == app.current_user['email']

                    # Remove the user's participation in the competition
                    cursor.execute("""
                    DELETE FROM user_competitions
                    WHERE competition_id = %s AND user_id = %s
                    """, (self.competition_id, app.current_user['email']))

                    rows_affected = cursor.rowcount
                    print(f"Rows affected by user removal: {rows_affected}")

                    if rows_affected > 0:
                        # Check if there are any remaining users in the competition
                        cursor.execute("""
                        SELECT user_id FROM user_competitions
                        WHERE competition_id = %s
                        ORDER BY user_id
                        LIMIT 1
                        """, (self.competition_id,))
                        remaining_user = cursor.fetchone()

                        if remaining_user:
                            if is_admin:
                                # Update the admin to the next user
                                new_admin = remaining_user['user_id']
                                cursor.execute("""
                                UPDATE competitions
                                SET admin_id = %s
                                WHERE competition_id = %s
                                """, (new_admin, self.competition_id))
                                print(f"New admin for competition {self.competition_id}: {new_admin}")
                        else:
                            # If no users left, remove the competition from the competitions table
                            cursor.execute("""
                            DELETE FROM competitions
                            WHERE competition_id = %s
                            """, (self.competition_id,))
                            print(f"Competition {self.competition_id} removed from competitions table")

                        # Commit the transaction
                        app.db_connection.commit()
                        print(f"Changes committed to the database")

                        print(f"User {app.current_user['email']} exited competition {self.competition_id}")

                        self.remove_bets_for_competition(app.current_user['email'], self.competition_id)

                        # Clear the entire cache
                        app.cache['competitions'].clear()
                        app.cache['screens'].clear()

                        # Switch to loading screen to reload data
                        app.switch_to_loading_screen()
                    else:
                        print(f"No rows affected. User might not be in the competition.")

                    # Print the current state of user_competitions for this competition
                    cursor.execute("""
                    SELECT * FROM user_competitions
                    WHERE competition_id = %s
                    """, (self.competition_id,))
                    current_state = cursor.fetchall()
                    print(f"Current state of user_competitions for competition {self.competition_id}:")
                    # for row in current_state:
                        # print(row)

            # Refresh the competition list
            if hasattr(app, 'refresh_competition_list'):
                app.refresh_competition_list()

        except Exception as e:
            print(f"Error exiting competition: {e}")
            app.db_connection.rollback()
            MDSnackbar(MDSnackbarText(text=app.get_translation("Error exiting competition. Please try again."))).open()

    def remove_bets_for_competition(self, user_email, competition_id):
        app = MDApp.get_running_app()
        try:
            db_path = os.path.join('user_databases', f'{user_email}_bets.db')
            print(f"Attempting to connect to SQLite database: {db_path}")

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Ensure the bets table exists
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competition_id TEXT,
                    match_date DATE,
                    match_teams TEXT,
                    bet_details TEXT,
                    UNIQUE(competition_id, match_date, match_teams)
                )
                ''')

                # Check if bets exist before deletion
                cursor.execute("""
                SELECT COUNT(*) FROM bets WHERE competition_id = ?
                """, (competition_id,))
                bet_count = cursor.fetchone()[0]
                print(f"Found {bet_count} bets for competition {competition_id}")

                # Delete all bets for the specified competition
                cursor.execute("""
                DELETE FROM bets WHERE competition_id = ?
                """, (competition_id,))

                rows_deleted = cursor.rowcount
                print(f"Deleted {rows_deleted} bets for competition {competition_id} from user {user_email}'s database")

                # Commit changes to SQLite database
                conn.commit()
                print("Changes committed to SQLite database")

        except sqlite3.Error as e:
            print(f"SQLite error in remove_bets_for_competition: {e}")
        except Exception as e:
            print(f"Unexpected error in remove_bets_for_competition: {e}")

"""
########################################
####### ManageCompetitionScreen ########
########################################
"""

class ManageCompetitionScreen(MDScreen):
    change_theme_text = StringProperty()
    languages_text = StringProperty()
    deconnect_text = StringProperty()
    contact_support_text = StringProperty()
    manage_competitions_text = StringProperty()
    join_competition_text = StringProperty()
    from_shared_id_text = StringProperty()
    enter_an_id_text = StringProperty()
    join_text = StringProperty()
    create_new_competition_text = StringProperty()
    name_text = StringProperty()
    enter_a_competition_name_text = StringProperty()
    select_a_type_of_competition_text = StringProperty()
    choose_the_rules_of_the_competition_text = StringProperty()
    contest_mode_text= StringProperty()
    open_contest_text = StringProperty()
    close_contest_text = StringProperty()
    duration_text = StringProperty()
    full_championship_season_text = StringProperty()
    first_leg_of_the_championship_text = StringProperty()
    full_championship_season_playoffs_text = StringProperty()
    second_leg_of_the_championship_text = StringProperty()
    second_leg_of_the_championship_playoffs_text = StringProperty()
    playoffs_text = StringProperty()
    predictions_method_text = StringProperty()
    match_score_text = StringProperty()
    winner_loser_text = StringProperty()
    awarding_points_method_text = StringProperty()
    bookmaker_quotes_text = StringProperty()
    point_scale_text = StringProperty()
    create_text = StringProperty()
    cancel_text = StringProperty()
    winner_text = StringProperty()
    winner_ot_text = StringProperty()
    loser_ot_text = StringProperty()
    loser_text = StringProperty()
    good_goal_difference_text = StringProperty()
    exact_score_regular_text = StringProperty()
    extra_score_extra_text = StringProperty()
    winner_regular_text = StringProperty()
    winner_extra_text = StringProperty()
    loser_regular_text = StringProperty()
    loser_extra_text = StringProperty()
    competition_created_successfully_text = StringProperty()
    competition_joined_successfully_text = StringProperty()
    selected_competition_type = StringProperty("Ligue Magnus")
    quit_text = StringProperty()
    share_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.menu = None
        # self.selected_competition_type = None
        self.active_switch = None
        self.point_scale_winner_loser = {
            'winner': 3,
            'winner_ot': 2,
            'loser_ot': 1,
            'loser': 0
        }
        self.point_scale_match_score = {
            'good_goal_difference': 1,
            'exact_score_regular': 4,
            'exact_score_extra': 3,
            'winner_regular': 2,
            'winner_extra': 1,
            'loser_regular': 0,
            'loser_extra': 0
        }
        self.update_translations()

    def update_translations(self):
        app = MDApp.get_running_app()
        self.change_theme_text = app.get_translation("Change Theme")
        self.languages_text = app.get_translation("Languages")
        self.deconnect_text = app.get_translation("Deconnect")
        self.contact_support_text = app.get_translation("Contact Support")
        self.manage_competitions_text = app.get_translation("Manage Competitions")
        self.join_competition_text = app.get_translation("Join Competition")
        self.from_shared_id_text = app.get_translation("From shared ID")
        self.enter_an_id_text = app.get_translation("Enter an ID")
        self.join_text = app.get_translation("Join")
        self.create_new_competition_text = app.get_translation("Create New Competition")
        self.name_text=app.get_translation("Name")
        self.enter_a_competition_name_text = app.get_translation("Enter a competition name")
        self.select_a_type_of_competition_text = app.get_translation("Select a type of competition")
        self.choose_the_rules_of_the_competition_text = app.get_translation("Choose the rules of the competition")
        self.contest_mode_text = app.get_translation("Contest Mode")
        self.open_contest_text = app.get_translation("Open Contest")
        self.close_contest_text = app.get_translation("Close Contest")
        self.duration_text = app.get_translation("Duration")
        self.full_championship_season_text = app.get_translation("Full championship season")
        self.first_leg_of_the_championship_text = app.get_translation("First leg of the championship")
        self.full_championship_season_playoffs_text = app.get_translation("Full championship season + Playoffs")
        self.second_leg_of_the_championship_text = app.get_translation("Second leg of the championship")
        self.second_leg_of_the_championship_playoffs_text = app.get_translation("Second leg of the championship season + Playoffs")
        self.playoffs_text = app.get_translation("Playoffs")
        self.predictions_method_text = app.get_translation("Predictions Method")
        self.match_score_text = app.get_translation("Match Score")
        self.winner_loser_text = app.get_translation("Winner / Loser")
        self.awarding_points_method_text = app.get_translation("Awarding Points Method")
        self.bookmaker_quotes_text = app.get_translation("Bookmaker Quotes")
        self.point_scale_text = app.get_translation("Point scale")
        self.create_text = app.get_translation("Create")
        self.cancel_text = app.get_translation("Cancel")
        self.winner_text = app.get_translation("winner")
        self.winner_ot_text = app.get_translation("winner_ot")
        self.loser_ot_text = app.get_translation("loser_ot")
        self.loser_text = app.get_translation("loser")
        self.good_goal_difference_text = app.get_translation("good_goal_difference")
        self.exact_score_regular_text = app.get_translation("exact_score_regular")
        self.extra_score_extra_text = app.get_translation("exact_score_extra")
        self.winner_regular_text = app.get_translation("winner_regular")
        self.winner_extra_text = app.get_translation("winner_extra")
        self.loser_regular_text = app.get_translation("loser_regular")
        self.loser_extra_text = app.get_translation("loser_extra")
        self.competition_created_successfully_text = app.get_translation("Competition created successfully")
        self.competition_joined_successfully_text = app.get_translation("Joined competition successfully")
        self.quit_text = app.get_translation("Quit")
        self.share_text = app.get_translation("Share")

    # à l'ouverture (when clicked on)
    def on_enter(self):
        self.create_competition_list()
        self.ids.winner_loser.active = True
        self.ids.point_scale.active = True
        self.update_awarding_points_method()

    # Tableau avec choix des points pour la competition
    # -------------------------------------------------
    def create_winner_loser_grid(self):
        # print("Creating winner/loser grid")
        grid = MDGridLayout(cols=4, spacing="8dp", adaptive_height=True)
        for key, value in self.point_scale_winner_loser.items():
            translated_key = self.app.get_translation(key)
            grid.add_widget(MDLabel(text=translated_key))
            grid.add_widget(
                MDIconButton(icon="minus", on_release=lambda x, k=key: self.decrement_point(k, 'winner_loser')))
            label = MDLabel(text=str(value))
            setattr(grid, f"{key}_points", label)  # Set the label as an attribute of the grid
            grid.add_widget(label)
            grid.add_widget(
                MDIconButton(icon="plus", on_release=lambda x, k=key: self.increment_point(k, 'winner_loser')))
        # print(f"Winner/loser grid created with {len(grid.children)} children")
        return grid

    def create_match_score_grid(self):
        # print("Creating match score grid")
        grid = MDGridLayout(cols=4, spacing="8dp", adaptive_height=True)
        for key, value in self.point_scale_match_score.items():
            translated_key = self.app.get_translation(key)
            grid.add_widget(MDLabel(text=translated_key))
            grid.add_widget(
                MDIconButton(icon="minus", on_release=lambda x, k=key: self.decrement_point(k, 'match_score')))
            label = MDLabel(text=str(value))
            setattr(grid, f"{key}_points", label)
            grid.add_widget(label)
            grid.add_widget(
                MDIconButton(icon="plus", on_release=lambda x, k=key: self.increment_point(k, 'match_score')))
        # print(f"Match score grid created with {len(grid.children)} children")
        return grid

    def increment_point(self, key, prediction_method):
        if prediction_method == 'winner_loser':
            self.point_scale_winner_loser[key] += 1
        else:
            self.point_scale_match_score[key] += 1
        self.update_point_scale_display(prediction_method)

    def decrement_point(self, key, prediction_method):
        if prediction_method == 'winner_loser':
            if self.point_scale_winner_loser[key] > 0:
                self.point_scale_winner_loser[key] -= 1
        else:
            if self.point_scale_match_score[key] > 0:
                self.point_scale_match_score[key] -= 1
        self.update_point_scale_display(prediction_method)

    def update_point_scale_display(self, prediction_method):
        grid = self.ids.tab_content.children[0]
        if prediction_method == 'winner_loser':
            for key, value in self.point_scale_winner_loser.items():
                label = getattr(grid, f"{key}_points", None)
                if label:
                    label.text = str(value)
        else:
            for key, value in self.point_scale_match_score.items():
                label = getattr(grid, f"{key}_points", None)
                if label:
                    label.text = str(value)

    def update_awarding_points_method(self):
        is_match_score = self.ids.match_score.active
        is_winner_loser = self.ids.winner_loser.active
        is_point_scale = self.ids.point_scale.active

        # Disable bookmaker quotes if match score is selected
        self.ids.bookmaker_quotes.disabled = is_match_score

        # If match score is selected, force point scale
        if is_match_score:
            self.ids.point_scale.active = True
            is_point_scale = True

        # Update point scale box visibility
        self.ids.point_scale_box.opacity = 1 if is_point_scale else 0
        self.ids.point_scale_box.disabled = not is_point_scale

        # Switch to the appropriate tab
        if is_point_scale:
            if is_winner_loser:
                self.ids.point_scale_tabs.switch_tab("Winner/Loser")
            else:
                self.ids.point_scale_tabs.switch_tab("Match Score")

            # Force update of tab content
            self.on_tab_switch(None, None, None, "Winner/Loser" if is_winner_loser else "Match Score")

        # print(f"Point scale active: {is_point_scale}")
        # print(f"Winner/Loser active: {is_winner_loser}")
        # print(f"Match Score active: {is_match_score}")
        # print(f"Point scale box opacity: {self.ids.point_scale_box.opacity}")
        # print(f"Point scale box disabled: {self.ids.point_scale_box.disabled}")

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        # print(f"Switching to tab: {tab_text}")
        self.ids.tab_content.clear_widgets()
        if tab_text == "Winner/Loser":
            grid = self.create_winner_loser_grid()
        elif tab_text == "Match Score":
            grid = self.create_match_score_grid()
        else:
            print(f"Unknown tab: {tab_text}")
            return

        self.ids.tab_content.add_widget(grid)
        # print(f"Added grid to tab_content: {grid}")

    # Boutons de choix de la compétition (LM, NL etc...)
    # --------------------------------------------------

    def on_segment_button_active_LM(self, segment_button):
        if segment_button.active:
            self.selected_competition_type = "Ligue Magnus"
            print(f"Selected competition type: {self.selected_competition_type}")  # Debug print

    def on_segment_button_active_NL(self, segment_button):
        if segment_button.active:
            self.selected_competition_type = "NL"
            print(f"Selected competition type: {self.selected_competition_type}")  # Debug print

    def on_segment_button_active_FourNations(self, segment_button):
        if segment_button.active:
            self.selected_competition_type = "Four Nations"
            print(f"Selected competition type: {self.selected_competition_type}")  # Debug print

    # Duration of the contest (season, playoffs etc..) using switches
    # ---------------------------------------------------------------

    def on_duration_switch(self, switch):
        print(f"on_duration_switch called with switch: {switch}")
        print(f"Switch state: {switch.active}")

        # If the switch is being activated
        if switch.active:
            # Deactivate all other switches
            for switch_id in ['full_season', 'first_leg', 'second_leg', 'full_season_playoffs', 'second_leg_playoffs',
                              'playoffs']:
                other_switch = self.ids.get(switch_id)
                if other_switch and other_switch != switch:
                    other_switch.active = False
            self.active_switch = switch
        else:
            # If trying to deactivate the only active switch, prevent it
            if self.active_switch == switch:
                switch.active = True
                return

        # Print final state only once
        Clock.schedule_once(lambda dt: self.print_final_state(), 0)

    def print_final_state(self):
        print("Final state of switches:")
        for switch_id in ['full_season', 'first_leg', 'second_leg', 'full_season_playoffs', 'second_leg_playoffs',
                          'playoffs']:
            switch = self.ids.get(switch_id)
            if switch:
                print(f"Switch {switch_id}: Active: {switch.active}")

    # Get the active switch to be identified in the competitions.json file
    #---------------------------------------------------------------------
    def get_active_duration(self):
        duration_mapping = {
            'full_season': "Full Season",
            'first_leg': "First Leg",
            'second_leg': "Second Leg",
            'full_season_playoffs': "Full Season Playoffs",
            'second_leg_playoffs': "Second Leg Playoffs",
            'playoffs': "Playoffs"
        }

        for switch_id, duration in duration_mapping.items():
            switch = self.ids.get(switch_id)
            if switch and switch.active:
                return duration

        return None

    # --------------------------
    # Create competition function
    # ---------------------------

    # Creation de la competition et écriture dans la base de données PostGreSQL
    # -------------------------------------------------------------------------

    def create_competition_list(self):
        competition_panel = self.ids.competition_panel
        competition_grid = competition_panel.ids.competition_grid
        competition_grid.clear_widgets()
        print("Clearing competition grid")

        with self.app.db_connection.cursor() as cursor:
            cursor.execute("""
            SELECT c.competition_id, c.name, c.type, c.duration, c.awarding_points_method, c.rules, c.contest_mode, c.admin_id, u.pseudo
            FROM competitions c
            JOIN user_competitions uc ON c.competition_id = uc.competition_id
            JOIN users u ON c.admin_id = u.user_id
            WHERE uc.user_id = %s
            """, (self.app.current_user['email'],))
            competitions = cursor.fetchall()
            print(f"Fetched competitions: {competitions}")

        for competition in competitions:
            rules_display = "Bookmaker Quotes" if competition['awarding_points_method'] == 'bookmaker_quotes' else str(
                competition['rules'])
            is_admin = competition['admin_id'] == self.app.current_user['email']

            try:
                card = CompetitionCard(
                    competition_name=competition['name'],
                    competition_type=competition['type'],
                    competition_id=competition['competition_id'],
                    competition_duration=competition['duration'],
                    competition_rules=rules_display,
                    contest_mode=competition['contest_mode'],
                    admin_pseudo=competition['pseudo'],
                    is_admin=is_admin
                )
                competition_grid.add_widget(card)
                print(f"Added card for competition: {competition['name']}")
            except Exception as e:
                print(f"Error creating CompetitionCard: {e}")

            # print(f"Card size: {card.size}")
            # print(f"Card pos: {card.pos}")

        print(f"Total cards added: {len(competition_grid.children)}")
        print(f"Competition grid size: {competition_grid.size}")
        print(f"Competition grid pos: {competition_grid.pos}")

    # Création de la compétition
    # --------------------------

    def create_competition(self):
        app = MDApp.get_running_app()
        competition_name = self.ids.create_competition_name.text
        competition_type = self.selected_competition_type
        contest_mode = "open" #if self.ids.open_contest.active else "closed"
        duration = self.get_active_duration()
        predictions_method = "match_score" if self.ids.match_score.active else "winner_loser"
        awarding_points_method = "bookmaker_quotes" if self.ids.bookmaker_quotes.active else "point_scale"

        if not competition_name or not competition_type or not duration:
            MDSnackbar(MDSnackbarText(text=app.get_translation("Please fill all fields and select a duration"))).open()
            return

        if predictions_method == "match_score" and awarding_points_method == "bookmaker_quotes":
            MDSnackbar(MDSnackbarText(text=app.get_translation("Bookmaker Quotes can only be used with Winner/Loser prediction method"))).open()
            return

        competition_id = str(uuid.uuid4())[:8]
        point_scale = self.point_scale_match_score if predictions_method == "match_score" else self.point_scale_winner_loser

        with self.app.db_connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO competitions (competition_id, name, type, contest_mode, duration, predictions_method, awarding_points_method, admin_id, matches_data, rankings_data, duration_filter, rules)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                competition_id, competition_name, competition_type, contest_mode, duration,
                predictions_method, awarding_points_method, self.app.current_user['email'],
                "ligue_magnus_matches.csv", "ligue_magnus_rankings.csv", duration,
                json.dumps({"point_scale": point_scale})
            ))

            cursor.execute("""
            INSERT INTO user_competitions (user_id, competition_id, points)
            VALUES (%s, %s, %s)
            """, (self.app.current_user['email'], competition_id, 0))

        self.app.db_connection.commit()

        self.create_competition_list()
        self.app.switch_to_loading_screen()
        MDSnackbar(MDSnackbarText(text=self.competition_created_successfully_text)).open()

    # Join competition function
    # -------------------------

    def join_competition(self):
        app = MDApp.get_running_app()
        competition_id = self.ids.join_competition_id.text

        if not competition_id:
            MDSnackbar(MDSnackbarText(text=app.get_translation("Please enter a competition ID"))).open()
            return

        with self.app.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM competitions WHERE competition_id = %s", (competition_id,))
            competition_data = cursor.fetchone()

            if not competition_data:
                MDSnackbar(MDSnackbarText(text=app.get_translation("Competition not found"))).open()
                return

            if competition_data['contest_mode'] == 'closed':
                cursor.execute("SELECT * FROM user_competitions WHERE competition_id = %s AND user_id = %s",
                               (competition_id, self.app.current_user['email']))
                if not cursor.fetchone():
                    MDSnackbar(MDSnackbarText(text=app.get_translation("This competition is closed"))).open()
                    return

            cursor.execute("""
            INSERT INTO user_competitions (user_id, competition_id, points)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, competition_id) DO NOTHING
            """, (self.app.current_user['email'], competition_id, 0))

        self.app.db_connection.commit()

        self.create_competition_list()
        self.app.switch_to_loading_screen()
        MDSnackbar(MDSnackbarText(text=self.competition_joined_successfully_text)).open()

    # Fonction de cancel, et retour au menu principal
    # ----------------------------------------------

    def cancel(self):
        self.app.switch_to_main_screen()

    def open_menu(self, button):
        app = MDApp.get_running_app()

        menu_items = [
            {
                "height": dp(56),
                "leading_icon": "theme-light-dark",
                "text": self.change_theme_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.change_theme_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "email",
                "text": self.contact_support_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.contact_support_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "translate",
                "text": self.languages_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.languages_text: self.menu_callback(x),
            },
            {
                "height": dp(56),
                "leading_icon": "logout",
                "text": self.deconnect_text,
                "trailing_icon": "chevron-right",
                "on_release": lambda x=self.deconnect_text: self.menu_callback(x),
            }
        ]

        if not self.menu or self.menu.caller != button:
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.menu.open()

    # Fonction de modifications des items aux seins des menus
    def menu_callback(self, text_item):
        app = MDApp.get_running_app()
        if text_item == self.change_theme_text:
            self.change_theme()
        elif text_item == self.contact_support_text:
            app.contact_support()
        elif text_item == self.deconnect_text:
            app.disconnect()
        elif text_item == self.languages_text:
            # Toggle between English and French
            app.current_language = 'fr' if app.current_language == 'en' else 'en'
            # Switch to changing language screen
            app.switch_to_changing_screen(self)
        self.menu.dismiss()

    # Fonction de mofication du thème
    def change_theme(self):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = (
            "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        )

'''
######################################
######### Classe principale  #########
######################################
'''

class HockeyProno(MDApp):
    background_image = StringProperty("image/Fond_ecran_noir_1.jpeg")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quotes = JsonStore('quotes.json')
        self.temp_password_file = 'temp_password.txt'
        self.current_user = None
        self.secure_storage = SecureStorage()
        self.matches_df_ligue_magnus = None
        self.rankings_df_ligue_magnus = None
        self.matches_df_nl = None
        self.rankings_df_nl = None
        self.matches_df_fournations = None
        self.rankings_df_fournations = None
        self.main_screen = None
        self.panels_added = False
        self.home_screen = None
        self.setup_profile_screen = None
        self.icon_selection_panel = None
        self.forgot_password_screen = None
        self.change_password_screen = None
        self.verification_pending_screen = None
        self.expansion_panel_item_connection = None
        self.expansion_panel_item_inscription = None
        self.expansion_panel_item_verification = None
        self.manage_competition_screen = None
        self.competition_card = None
        self.list_of_your_competition_panel = None
        self.match_widget_winner_loser = None
        self.match_widget_match_score = None
        self.base_screen_lm_classement = None
        self.base_screen_lm_rankings = None
        self.competition_screen_lm = None
        self.base_screen_nl_classement = None
        self.base_screen_nl_rankings = None
        self.competition_screen_nl = None
        self.base_screen_fournations_classement = None
        self.base_screen_fournations_rankings = None
        self.competition_screen_fournations = None
        self.loading_screen = None
        self.cache = {
            'competitions': {},
            'screens': {}
        }
        self.connect_to_db()
        self.connect_to_sqlite()
        self.current_language = 'en'  # Default language
        self.load_translations()

    def load_translations(self):
        with open('translations.json', 'r', encoding='utf-8') as file:
            self.translations = json.load(file)

    def get_translation(self, text):
        return self.translations[self.current_language].get(text, text)

    def update_ui_language(self):
        self.setup_profile_screen = SetupProfileScreen()
        self.icon_selection_panel = IconSelectionPanel()
        self.forgot_password_screen = ForgotPasswordScreen()
        self.change_password_screen = ChangePasswordScreen()
        self.verification_pending_screen = VerificationPendingScreen()
        self.home_screen = HomeScreen()
        self.expansion_panel_item_connection = ExpansionPanelItemConnection()
        self.expansion_panel_item_inscription = ExpansionPanelItemInscription()
        self.expansion_panel_item_verification = ExpansionPanelItemVerification()
        self.main_screen = MainScreen()
        self.manage_competition_screen = ManageCompetitionScreen()
        self.competition_card = CompetitionCard
        self.list_of_your_competition_panel = ListOfYourCompetitionPanel()
        self.match_widget_winner_loser = MatchWidgetWinnerLoser()
        self.match_widget_match_score = MatchWidgetMatchScore()
        self.base_screen_lm_classement = BaseScreenLM_Classement()
        self.base_screen_lm_rankings = BaseScreenLM_Rankings()
        self.base_screen_nl_classement = BaseScreenNL_Classement()
        self.base_screen_nl_rankings = BaseScreenNL_Rankings()
        self.base_screen_fournations_classement = BaseScreenNL_Classement()
        self.base_screen_fournations_rankings = BaseScreenNL_Rankings()
        self.main_home = MainHome
        self.competition_screen_lm = CompetitionScreenLM()
        self.competition_screen_nl = CompetitionScreenNL()
        self.competition_screen_fournations = CompetitionScreenFourNations()
        self.loading_screen = LoadingScreen()
        screens_to_update = [
            self.setup_profile_screen, self.icon_selection_panel,
            self.forgot_password_screen, self.change_password_screen,
            self.verification_pending_screen, self.home_screen,
            self.expansion_panel_item_connection, self.expansion_panel_item_inscription,
            self.expansion_panel_item_verification, self.main_screen,
            self.manage_competition_screen, self.list_of_your_competition_panel,
            self.match_widget_winner_loser, self.match_widget_match_score,
            self.base_screen_lm_classement, self.base_screen_lm_rankings,
            self.base_screen_nl_classement, self.base_screen_nl_rankings,
            self.base_screen_fournations_classement, self.base_screen_fournations_rankings,
            self.main_home, self.competition_screen_lm, self.competition_screen_nl,
            self.competition_screen_fournations, self.loading_screen
        ]

        for screen in screens_to_update:
            if screen and isinstance(screen, Widget):
                self.update_screen_language(screen)

    def update_screen_language(self, screen):
        if isinstance(screen, Widget):
            for widget in screen.walk():
                if hasattr(widget, 'text'):
                    widget.text = self.get_translation(widget.text)

    def perform_language_update(self, previous_screen_type):
        self.update_ui_language()
        # Switch back to the appropriate screen
        if previous_screen_type == 'HomeScreen':
            self.switch_to_home_screen()
        elif previous_screen_type == 'MainScreen':
            self.switch_to_main_screen()
        elif previous_screen_type == 'ManageCompetitionScreen':
            self.switch_to_manage_competition_screen()
        elif previous_screen_type == 'SetupProfileScreen':
            self.switch_to_setup_profile()

        # else:
        #     # Default to home screen if the type is unknown
        #     self.switch_to_home_screen()

        self.show_snackbar(self.get_translation("Language changed to {language}").format(
            language=self.get_translation("Français") if self.current_language == 'fr' else self.get_translation(
                "English")
        ))

    #################
    # Notifications #
    #################

    def create_notification_channel(self):
        Context = autoclass('android.content.Context')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')

        channel_id = "my_channel_id"
        channel_name = "My Notification Channel"
        importance = NotificationManager.IMPORTANCE_DEFAULT

        channel = NotificationChannel(channel_id, channel_name, importance)
        notification_manager = Context.getSystemService(Context.NOTIFICATION_SERVICE)
        notification_manager.createNotificationChannel(channel)

    def show_notification(self, title, message):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Notification = autoclass('android.app.Notification')
        Builder = autoclass('android.app.Notification$Builder')

        context = PythonActivity.mActivity.getApplicationContext()
        builder = Builder(context, "my_channel_id")
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setSmallIcon(context.getApplicationInfo().icon)

        notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        notification_manager.notify(1, builder.build())

    ##########
    # Listes #
    ##########

    team_icons = {

        # Ligue Magnus
        "ANGERS": "owl",
        "ROUEN": "google-downasaur",
        "GRENOBLE": "fire",
        "AMIENS": "bat",
        "BORDEAUX": "dog",
        "MARSEILLE": "sword-cross",
        "CERGY": "cards-playing-club",
        "NICE": "alpha-n-circle",
        "ANGLET": "tsunami",
        "CHAMONIX": "hammer",
        "GAP": "bird",
        "BRIANCON": "emoticon-devil",

        # NL
        "Davos": "alpha-d-circle",
        "Zurich": "alpha-z-circle",
        "Lausanne": "alpha-l-circle",
        "Berne": "alpha-b-circle",
        "Kloten": "alpha-k-circle",
        "Zoug": "alpha-z-circle",
        "Bienne": "alpha-b-circle",
        "Ambri": "alpha-a-circle",
        "Fribourg": "alpha-f-circle",
        "Langnau": "alpha-l-circle",
        "Geneve": "alpha-g-circle",
        "Lugano": "alpha-l-circle",
        "Rapperswil": "alpha-r-circle",
        "Ajoie": "google-downasaur",

        # 4 Nations
        "Canada": "leaf-maple",
        "Sweden": "crown",
        "Finland": "alpha-f-circle",
        "USA": "account-cowboy-hat"
    }

    # Fonctions de connexions aux bases de données
    # ---------------------------------------------

    # Base de données PostGreSQL
    def connect_to_db(self):
        try:
            self.db_connection = psycopg2.connect(
                host="localhost",
                database="hockey_prono_db",
                user="postgres",
                password="DiaboloValier+1241",
                cursor_factory=RealDictCursor
            )
            # print("Connected to PostgreSQL database successfully")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            self.db_connection = None

    # Base de données SQLite
    def connect_to_sqlite(self):
        self.sqlite_connections = {}
        user_db_folder = 'user_databases'
        if not os.path.exists(user_db_folder):
            os.makedirs(user_db_folder)
        for filename in os.listdir(user_db_folder):
            if filename.endswith('_bets.db'):
                user_id = filename[:-8]  # Remove '_bets.db' from the filename
                db_path = os.path.join(user_db_folder, filename)
                self.sqlite_connections[user_id] = sqlite3.connect(db_path)
        print("Connected to SQLite databases successfully")

    # A l'ouverture
    ###############

    # Création du thème et ouverture du HomeScreen à l'ouverture
    def build(self):
        self.load_translations()
        self.create_notification_channel()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.primary_Color = "Cyan"
        self.theme_cls.background_color = "Grey"
        self.theme_cls.shadow_color = "Custom"
        self.home_screen = HomeScreen(name='home')

        # Bind the theme_style to update_background method
        self.theme_cls.bind(theme_style=self.update_background)

        #Fonts
        LabelBase.register(name="RacingSansOne", fn_regular="fonts/RacingSansOne-Regular.ttf")
        LabelBase.register(name="Electrolize", fn_regular="fonts/Electrolize-Regular.ttf")
        LabelBase.register(name="Nunito", fn_regular="fonts/NunitoSans_10pt-MediumItalic.ttf")

        return self.home_screen

    def update_background(self, *args):
        # Use Clock.schedule_once to ensure this runs in the next frame
        Clock.schedule_once(self._update_background, 0)

    def _update_background(self, dt):
        if self.theme_cls.theme_style == "Dark":
            self.background_image = "image/Fond_ecran_noir_1.jpeg"
        else:
            self.background_image = "image/glace_fond_ecran_2.jpeg"

    # Fonction d'initialisation des ExpansionPanel de connection et d'inscription
    def on_start(self):
        self.load_csv_data_ligue_magnus()
        self.load_csv_data_nl()
        self.load_csv_data_fournations()
        self.load_translations()

        async def set_panel_list():
            await asynckivy.sleep(0)
            self.root.ids.container.add_widget(ExpansionPanelItemConnection())
            self.root.ids.container.add_widget(ExpansionPanelItemInscription())
            self.root.ids.container.add_widget(ExpansionPanelItemVerification())
        asynckivy.start(set_panel_list())

    ################
    ## HomeScreen ##
    ################

    ########################
    # Bouton forgot password
    ########################

    def change_password(self, email, temp_password, new_password, confirm_new_password):
        print(f"Attempting to change password for email: {email}")
        print(f"Temp password: {temp_password}")
        print(f"New password: {new_password}")
        print(f"Confirm new password: {confirm_new_password}")

        if not email or not temp_password or not new_password or not confirm_new_password:
            print("Missing required fields")
            self.show_snackbar(self.get_translation("Please fill in all fields"))
            return

        # Remove trimming and lowercase conversion
        if new_password != confirm_new_password:
            print("New passwords do not match")
            self.show_snackbar(self.get_translation("New passwords do not match"))
            return

        try:
            with self.db_connection.cursor() as cursor:
                print("Executing database query")
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cursor.fetchone()

                print(f"User data retrieved: {user_data}")

                if not user_data:
                    print("Invalid email - user not found")
                    self.show_snackbar(self.get_translation("Invalid email"))
                    return

                print("Verifying temporary password")
                if not self.verify_temp_password(email, temp_password):
                    print("Invalid temporary password")
                    self.show_snackbar(self.get_translation("Invalid temporary password"))
                    return

                print("Validating new password")
                try:
                    self.secure_storage.validate_password(new_password)
                except ValueError as e:
                    print(f"Invalid new password: {e}")
                    self.show_snackbar(str(e))
                    return

                print("Changing password")
                hashed_new_password = self.secure_storage.hash_password(new_password)
                print(f"Hashed new password: {hashed_new_password}")
                self.secure_storage.store_password(email, hashed_new_password)

                print("Removing temporary password")
                self.remove_temp_password(email)

            print("Password changed successfully")
            self.show_snackbar(self.get_translation("Password changed successfully"))

            # Update the current user data
            self.update_current_user(email)

            # Use Clock to schedule the screen switch
            Clock.schedule_once(lambda dt: self.switch_to_main_screen(), 1)

        except Exception as e:
            print(f"Error changing password: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")
            self.show_snackbar(self.get_translation("Error changing password. Please try again."))

    def update_current_user(self, email):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data:
                self.current_user = dict(user_data)
                print(f"Updated current user: {self.current_user}")

    def store_temp_password(self, email, temp_password):
        temp_passwords = {}
        if os.path.exists(self.temp_password_file):
            with open(self.temp_password_file, 'r') as file:
                temp_passwords = json.load(file)

        temp_passwords[email] = temp_password

        with open(self.temp_password_file, 'w') as file:
            json.dump(temp_passwords, file)

    def handle_forgot_password(self, email):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cursor.fetchone()

                if not user_data:
                    self.show_snackbar(self.get_translation("Email not found"))
                    return

                temp_password = self.generate_temporary_password()

                try:
                    self.send_email(email, temp_password)

                    # Store the temporary password in the file
                    self.store_temp_password(email, temp_password)

                    self.show_snackbar(self.get_translation("Temporary password sent to your email"))
                except Exception as e:
                    print(f"Error sending email: {e}")
                    self.show_snackbar(self.get_translation("Error sending email. Please try again later."))

        except Exception as e:
            print(f"Error handling forgot password: {e}")
            self.show_snackbar(self.get_translation("Error processing request. Please try again."))

    def verify_temp_password(self, email, temp_password):
        if os.path.exists(self.temp_password_file):
            with open(self.temp_password_file, 'r') as file:
                temp_passwords = json.load(file)
                return temp_passwords.get(email) == temp_password
        return False

    def remove_temp_password(self, email):
        if os.path.exists(self.temp_password_file):
            with open(self.temp_password_file, 'r') as file:
                temp_passwords = json.load(file)

            if email in temp_passwords:
                del temp_passwords[email]

            with open(self.temp_password_file, 'w') as file:
                json.dump(temp_passwords, file)

    def generate_temporary_password(self):
        # Create a custom character set without 'l' and 'I'
        char_set = string.ascii_letters + string.digits
        char_set = char_set.replace('l', '').replace('I', '')

        # Generate an 8-character password
        return ''.join(random.choices(char_set, k=8))

    def send_email(self, to_email, temp_password):
        sender_email = "noreplybetpuck@gmail.com"
        sender_password = "ehem ykun gyda nfgq"  # Make sure to use an app password

        message = MIMEMultipart()
        message["Subject"] = "Hockey Prono temporary password"
        message["From"] = sender_email
        message["To"] = to_email

        body = f"""\
    Dear User,

    Your temporary password for HockeyProno is: {temp_password}

    Please enter this password in the app to log in and set a new password.

    This is an automatic message. Please do not reply to it.

    Best regards,
    The HockeyProno Team
    """

        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, to_email, message.as_string())
            print(f"Temporary password email sent successfully to {to_email}")
        except Exception as e:
            print(f"Error sending temporary password email: {e}")
            raise  # Re-raise the exception to be caught in the calling function

    #############################
    ## Verification adresse email
    #############################

    def verify_email_code(self, email, entered_code):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cursor.fetchone()

                if not user_data:
                    self.show_snackbar(self.get_translation("Email not found"))
                    return False

                if user_data['is_verified']:
                    self.show_snackbar(self.get_translation("Email is already verified"))
                    return False

                if self.check_verification_code(email, entered_code):
                    cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = %s", (email,))
                    self.db_connection.commit()
                    self.clear_verification_code(email)
                    self.switch_to_setup_profile()
                    return True
                else:
                    self.show_snackbar(self.get_translation("Invalid verification code"))
                    return False
        except Exception as e:
            print(f"Error verifying email code: {e}")
            self.db_connection.rollback()
            self.show_snackbar(self.get_translation("Error verifying email. Please try again."))
            return False

    def check_verification_code(self, email, code):
        with open('verification_codes.txt', 'r') as f:
            for line in f:
                stored_email, stored_code = line.strip().split(':')
                if stored_email == email and stored_code == code:
                    return True
        return False

    def resend_verification_email(self, email):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cursor.fetchone()

                if not user_data:
                    self.show_snackbar(self.get_translation("Email not found"))
                    return

                verification_code = self.generate_verification_code()
                self.store_verification_code(email, verification_code)
                self.send_verification_email(email, verification_code)
                self.show_snackbar(self.get_translation("Verification email resent. Please check your inbox."))
        except Exception as e:
            print(f"Error resending verification email: {e}")
            self.show_snackbar(self.get_translation("Error resending verification email. Please try again later."))

    def clear_verification_code(self, email):
        with open('verification_codes.txt', 'r') as f:
            lines = f.readlines()
        with open('verification_codes.txt', 'w') as f:
            for line in lines:
                stored_email, _ = line.strip().split(':')
                if stored_email != email:
                    f.write(line)

    # bjew ljgt qerb wnmw
    def generate_verification_code(self):
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def store_verification_code(self, email, code):
        with open('verification_codes.txt', 'a') as f:
            f.write(f"{email}:{code}\n")

    def resend_verification_code(self, email):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user_data = cursor.fetchone()

                if not user_data:
                    self.show_snackbar(self.get_translation("Email not found"))
                    return

                verification_code = self.generate_verification_code()
                self.store_verification_code(email, verification_code)
                self.send_verification_email(email, verification_code)
                self.show_snackbar(self.get_translation("Verification code sent. Please check your email."))
        except Exception as e:
            print(f"Error sending verification email: {e}")
            self.show_snackbar(self.get_translation("Error sending verification email. Please try again later."))

    def send_verification_email(self, email, verification_code):
        sender_email = "noreplybetpuck@gmail.com"
        sender_password = "ehem ykun gyda nfgq"  # Make sure to use an app password

        message = MIMEMultipart()
        message["Subject"] = "Verify your HockeyProno account"
        message["From"] = sender_email
        message["To"] = email

        body = f"""\
    Dear User,

    Your verification code for HockeyProno is: {verification_code}

    Please enter this code in the app to verify your account.

    This is an automatic message. Please do not reply to it.
    """

        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())
            print(f"Verification email sent successfully to {email}")
        except Exception as e:
            print(f"Error sending verification email: {e}")
            raise  # Re-raise the exception to be caught in the calling function

    #################################
    ## Expansion Panels du HomeScreen
    #################################

    # Fonction d'inscription du user
    def register_user(self):
        print("Starting register_user function")
        print(f"self.home_screen: {self.home_screen}")
        print(f"self.root: {self.root}")

        if not self.home_screen:
            print("HomeScreen not found, creating a new one")
            self.home_screen = HomeScreen(name='home')
            if isinstance(self.root, MDScreenManager):
                self.root.add_widget(self.home_screen)
            else:
                self.root = self.home_screen

        print(f"HomeScreen instance: {self.home_screen}")
        print(f"HomeScreen ids: {self.home_screen.ids}")

        if 'container' not in self.home_screen.ids:
            print("Container not found in HomeScreen ids")
            return

        container = self.home_screen.ids.container
        print(f"Container: {container}")

        register_panel = None
        for child in container.children:
            print(f"Child: {child}")
            if isinstance(child, ExpansionPanelItemInscription):
                register_panel = child
                break

        if not register_panel:
            print("Registration panel not found")
            self.show_snackbar(self.get_translation("Registration panel not found"))
            return

        print("Attempting to access registration fields")
        try:
            email = register_panel.ids.register_email.text
            password = register_panel.ids.register_password.text
            confirm_password = register_panel.ids.confirm_password.text
            print(f"Email: {email}, Password: {'*' * len(password)}, Confirm Password: {'*' * len(confirm_password)}")
        except Exception as e:
            print(f"Error accessing registration fields: {e}")
            return

        if not email or not password or not confirm_password:
            print("One or more fields are empty")
            self.show_snackbar(self.get_translation("Please fill in all fields"))
            return

        if password != confirm_password:
            print("Passwords do not match")
            self.show_snackbar(self.get_translation("Passwords do not match"))
            return

        # Validate password format
        try:
            self.secure_storage.validate_password(password)
        except ValueError as e:
            print(f"Invalid password format: {e}")
            self.show_snackbar(str(e))
            return

        # Check if user already exists
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print("Email already registered")
                self.show_snackbar(self.get_translation("Email already registered"))
                return

        print("Registering new user")
        hashed_password = self.secure_storage.hash_password(password)
        verification_code = self.generate_verification_code()

        # Insert new user into the database
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (user_id, email, icon, is_verified, pseudo) VALUES (%s, %s, %s, %s, %s)",
                (email, email, 'account-box', False, '')
            )
            self.db_connection.commit()

        # Store password in secure storage
        try:
            self.secure_storage.store_password(email, hashed_password)
        except Exception as e:
            print(f"Error storing password: {e}")
            self.show_snackbar(self.get_translation("Error storing password. Please try again."))
            return

        # Store verification code
        self.store_verification_code(email, verification_code)

        # Send verification email
        try:
            self.send_verification_email(email, verification_code)
            self.show_snackbar(
                self.get_translation("Registration successful. Please check your email for the verification code."))
        except Exception as e:
            print(f"Error sending verification email: {e}")
            self.show_snackbar(self.get_translation(
                "Registration successful, but there was an error sending the verification email. Please contact support."))

        self.current_user = {'email': email, 'icon': 'account-box', 'is_verified': False}
        print("Switching to verification pending screen")
        self.switch_to_verification_pending_screen()

    # Fonction de login du user
    def login_user(self):
        print("Starting login_user function")
        print(f"self.home_screen: {self.home_screen}")
        print(f"self.root: {self.root}")

        if not self.home_screen:
            print("HomeScreen not found, creating a new one")
            self.home_screen = HomeScreen(name='home')
            if isinstance(self.root, MDScreenManager):
                self.root.add_widget(self.home_screen)
            else:
                self.root = self.home_screen

        print(f"HomeScreen instance: {self.home_screen}")
        print(f"HomeScreen ids: {self.home_screen.ids}")

        if 'container' not in self.home_screen.ids:
            print("Container not found in HomeScreen ids")
            return

        container = self.home_screen.ids.container
        print(f"Container: {container}")

        login_panel = None
        for child in container.children:
            print(f"Child: {child}")
            if isinstance(child, ExpansionPanelItemConnection):
                login_panel = child
                break

        if not login_panel:
            print("Login panel not found")
            self.show_snackbar(self.get_translation("Login panel not found"))
            return

        print("Attempting to access login_email and login_password")
        try:
            email = login_panel.ids.login_email.text
            password = login_panel.ids.login_password.text
            print(f"Email: {email}, Password: {'*' * len(password)}")
        except Exception as e:
            print(f"Error accessing login fields: {e}")
            return

        if not email or not password:
            print("Email or password is empty")
            self.show_snackbar(self.get_translation("Please fill in all fields"))
            return

        # Validate password format before checking against stored password
        try:
            self.secure_storage.validate_password(password)
        except ValueError as e:
            print(f"Invalid password format: {e}")
            self.show_snackbar(str(e))
            return

        # Check user in database
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()

        if not user_data:
            print("Invalid email or password")
            self.show_snackbar(self.get_translation("Invalid email or password"))
            return

        if not user_data['is_verified']:
            print("Email not verified")
            self.show_snackbar(self.get_translation("Please verify your email before logging in."))
            return

        try:
            stored_password = self.secure_storage.get_password(email)
            if not stored_password or not self.secure_storage.verify_password(stored_password, password):
                print("Invalid email or password")
                self.show_snackbar(self.get_translation("Invalid email or password"))
                return
        except Exception as e:
            print(f"Error during password verification: {e}")
            self.show_snackbar(self.get_translation("An error occurred during login. Please try again."))
            return

        print("Login successful")
        self.show_snackbar(self.get_translation("Login successful"))
        self.current_user = user_data

        print("Switching to Loading Screen")
        self.switch_to_loading_screen()

    ###################
    ## Load csv data ##
    ###################
    # Fonction de chargement des données csv stockées sur GitHub LigueMagnus
    def load_csv_data_ligue_magnus(self):
        print(f"Memory usage before loading CSV: {memory_usage() / 1024 / 1024:.2f} MB")

        base_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/"
        files = ["ligue_magnus_matches.csv", "ligue_magnus_rankings.csv"]

        french_months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }

        def parse_french_date(date_str):
            day, month, year = date_str.split()
            month_num = french_months[month.lower()]
            return datetime(int(year), month_num, int(day))

        for file in files:
            url = base_url + file
            response = requests.get(url)
            if response.status_code == 200:
                if file == "ligue_magnus_matches.csv":
                    self.matches_df_ligue_magnus = pd.read_csv(io.StringIO(response.text))
                    # Parse dates using the custom function
                    self.matches_df_ligue_magnus['date'] = self.matches_df_ligue_magnus['date'].apply(parse_french_date)
                elif file == "ligue_magnus_rankings.csv":
                    self.rankings_df_ligue_magnus = pd.read_csv(io.StringIO(response.text))
                print(f"Loaded {file}")
            else:
                print(f"Failed to download {file}")

        # Debug print
        # print("Parsed dates:")
        # print(self.matches_df_ligue_magnus['date'].head())

    # Fonction de chargement des données csv stockées sur GitHub NL
    def load_csv_data_nl(self):
        print(f"Memory usage before loading CSV: {memory_usage() / 1024 / 1024:.2f} MB")

        base_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/"
        files = ["nl_matches.csv", "nl_rankings.csv"]

        french_months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }

        def parse_french_date(date_str):
            day, month, year = date_str.split()
            month_num = french_months[month.lower()]
            return datetime(int(year), month_num, int(day))

        for file in files:
            url = base_url + file
            response = requests.get(url)
            if response.status_code == 200:
                if file == "nl_matches.csv":
                    self.matches_df_nl = pd.read_csv(io.StringIO(response.text))
                    # Parse dates using the custom function
                    self.matches_df_nl['date'] = self.matches_df_nl['date'].apply(parse_french_date)
                elif file == "nl_rankings.csv":
                    self.rankings_df_nl = pd.read_csv(io.StringIO(response.text))
                print(f"Loaded {file}")
            else:
                print(f"Failed to download {file}")

        # Debug print
        print("Parsed dates:")
        print(self.matches_df_nl['date'].head())

    def load_csv_data_fournations(self):
        print(f"Memory usage before loading CSV: {memory_usage() / 1024 / 1024:.2f} MB")

        base_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/"
        files = ["fournations_matches.csv", "fournations_rankings.csv"]

        french_months = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }

        def parse_french_date(date_str):
            day, month, year = date_str.split()
            month_num = french_months[month.lower()]
            return datetime(int(year), month_num, int(day))

        for file in files:
            url = base_url + file
            response = requests.get(url)
            if response.status_code == 200:
                if file == "fournations_matches.csv":
                    self.matches_df_fournations = pd.read_csv(io.StringIO(response.text))
                    self.matches_df_fournations['date'] = self.matches_df_fournations['date'].apply(parse_french_date)
                elif file == "fournations_rankings.csv":
                    self.rankings_df_fournations = pd.read_csv(io.StringIO(response.text))
                print(f"Loaded {file}")
            else:
                print(f"Failed to download {file}")

        print("Parsed dates:")
        print(self.matches_df_fournations['date'].head())

    #############
    ## Filtres ##
    #############

    def filter_matches_by_duration(self, matches_df, duration):
        # Ensure the date column is in datetime format
        matches_df['date'] = pd.to_datetime(matches_df['date'])

        # Filter based on duration
        if duration == "Playoffs":
            filtered_df = matches_df[matches_df['leg'] == 'Playoffs']
            if filtered_df.empty:
                print("No playoff matches available yet.")
                filtered_df = pd.DataFrame(columns=matches_df.columns).astype(matches_df.dtypes)
        elif duration == "Full Season":
            filtered_df = matches_df[matches_df['leg'].isin(['First Leg', 'Second Leg'])]
        elif duration == "First Leg":
            filtered_df = matches_df[matches_df['leg'] == 'First Leg']
        elif duration == "Second Leg":
            filtered_df = matches_df[matches_df['leg'] == 'Second Leg']
        elif duration == "Full Season Playoffs":
            filtered_df = matches_df[matches_df['leg'].isin(['First Leg', 'Second Leg', 'Playoffs'])]
        elif duration == "Second Leg Playoffs":
            filtered_df = matches_df[matches_df['leg'].isin(['Second Leg', 'Playoffs'])]
        else:
            filtered_df = matches_df  # Return full DataFrame if duration is not recognized

        return filtered_df

    # Fonction de filtration des matches avec les données bookmakers
    def filter_matches_for_bookmaker_quotes(self, matches_df):
        teams_occurrences = {}
        filtered_matches = []

        for _, match in matches_df.iterrows():
            team1, team2 = match['match'].split(' - ')

            if team1 not in teams_occurrences:
                teams_occurrences[team1] = 0
            if team2 not in teams_occurrences:
                teams_occurrences[team2] = 0

            if teams_occurrences[team1] == 0 or teams_occurrences[team2] == 0:
                filtered_matches.append(match)
                teams_occurrences[team1] += 1
                teams_occurrences[team2] += 1

        return pd.DataFrame(filtered_matches)

    # Fonction de filtration des matches avec attribution des points par point scale
    def filter_matches_for_point_scale(self, matches_df):
        team_occurrences = {}
        filtered_matches = []

        for _, match in matches_df.iterrows():
            team1, team2 = match['match'].split(' - ')

            if team1 not in team_occurrences:
                team_occurrences[team1] = 0
            if team2 not in team_occurrences:
                team_occurrences[team2] = 0

            if team_occurrences[team1] == 0 or team_occurrences[team2] == 0:
                filtered_matches.append(match)
                team_occurrences[team1] += 1
                team_occurrences[team2] += 1

        return pd.DataFrame(filtered_matches)

    # Interaction avec les JSON files
    #################################

    # Fonction d'ajout de la compétition dans database PostGreSQL
    def add_competition_to_user(self, competition_id, competition_data):
        with self.db_connection.cursor() as cursor:
            # Add to user_competitions table
            cursor.execute("""
            INSERT INTO user_competitions (user_id, competition_id, points)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, competition_id) DO NOTHING
            """, (self.current_user['email'], competition_id, 0))

            # Add to competition_rules table
            rules = {
                'contest_mode': competition_data['contest_mode'],
                'duration': competition_data['duration'],
                'predictions_method': competition_data['predictions_method'],
                'awarding_points_method': competition_data['awarding_points_method']
            }
            if competition_data["awarding_points_method"] == "point_scale" and "point_scale" in competition_data:
                rules["point_scale"] = competition_data["point_scale"]

            for rule_key, rule_value in rules.items():
                cursor.execute("""
                INSERT INTO competition_rules (competition_id, rule_key, rule_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (competition_id, rule_key) DO UPDATE SET rule_value = EXCLUDED.rule_value
                """, (competition_id, rule_key, json.dumps(rule_value)))

        self.db_connection.commit()
        print(f"Competition {competition_id} added to user {self.current_user['email']}")

    # Fonction d'ajout d'un user à la table competition et user_competition de la base de données PostGreSQL

    def add_user_to_competition(self, competition_id, user_email):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM competitions WHERE competition_id = %s", (competition_id,))
            competition_data = cursor.fetchone()

            if competition_data:
                cursor.execute("""
                INSERT INTO user_competitions (user_id, competition_id, points)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, competition_id) DO NOTHING
                """, (user_email, competition_id, 0))

                if competition_data['type'] == "Ligue Magnus":
                    cursor.execute("""
                    UPDATE competitions
                    SET matches_data = %s, rankings_data = %s, duration_filter = %s
                    WHERE competition_id = %s
                    """, ("ligue_magnus_matches.csv", "ligue_magnus_rankings.csv", competition_data["duration"],
                          competition_id))

                self.db_connection.commit()
                print(f"User {user_email} added to competition {competition_id}")
            else:
                print(f"Competition {competition_id} not found")

    # Chargement des competitions
    #############################

    # Fonction de chargement des competitions au sein du loading screen (parent)
    def load_all_user_competitions(self, *args):
        print("Loading all user competitions")
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
            SELECT c.* FROM competitions c
            JOIN user_competitions uc ON c.competition_id = uc.competition_id
            WHERE uc.user_id = %s
            """, (self.current_user['email'],))
            competitions = cursor.fetchall()

            for competition in competitions:
                competition_id = competition['competition_id']
                if competition_id not in self.cache['competitions']:
                    full_competition_data = self.load_competition(competition_id)
                    if full_competition_data:
                        self.cache['competitions'][competition_id] = full_competition_data

        print(f"Loaded competitions: {list(self.cache['competitions'].keys())}")
        print(f"Cache after loading: {self.cache['competitions'].keys()}")

    def load_competition(self, competition_id):
        if competition_id in self.cache['competitions']:
            print(f"Using cached data for competition with id: {competition_id}")
            return self.cache['competitions'][competition_id]

        # print(f"Loading competition with id: {competition_id}")
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM competitions WHERE competition_id = %s", (competition_id,))
            competition_data = cursor.fetchone()

            if competition_data:
                if competition_data["type"] in ["Ligue Magnus", "NL"]:
                    if competition_data["type"] == "Ligue Magnus":
                        if self.matches_df_ligue_magnus is None or self.rankings_df_ligue_magnus is None:
                            self.load_csv_data_ligue_magnus()
                        matches_df = self.matches_df_ligue_magnus
                        rankings_df = self.rankings_df_ligue_magnus
                    else:  # NL
                        if self.matches_df_nl is None or self.rankings_df_nl is None:
                            self.load_csv_data_nl()
                        matches_df = self.matches_df_nl
                        rankings_df = self.rankings_df_nl

                    duration_filter = competition_data.get("duration_filter", "Full Season Playoffs")
                    filtered_matches = self.filter_matches_by_duration(matches_df, duration_filter)
                elif competition_data["type"] == "Four Nations":
                    if self.matches_df_fournations is None or self.rankings_df_fournations is None:
                        self.load_csv_data_fournations()
                    matches_df = self.matches_df_fournations
                    rankings_df = self.rankings_df_fournations
                    filtered_matches = matches_df  # No duration filter for Four Nations
                else:
                    print(f"Unsupported competition type: {competition_data['type']}")
                    return None

                full_competition_data = dict(competition_data)
                full_competition_data["rankings_data"] = rankings_df.to_dict('records')
                full_competition_data["matches_data"] = matches_df.to_dict('records')

                today = datetime.now().date()
                upcoming_matches = filtered_matches[
                    (filtered_matches['date'].dt.date >= today) &
                    (filtered_matches['available'] == 'yes')
                    ].sort_values('date')

                awarding_points_method = competition_data.get("awarding_points_method", "point_scale")
                if awarding_points_method == "bookmaker_quotes":
                    upcoming_matches = self.filter_matches_for_bookmaker_quotes(upcoming_matches)
                else:  # point_scale
                    upcoming_matches = self.filter_matches_for_point_scale(upcoming_matches)

                rules = competition_data.get('rules', {})
                if isinstance(rules, str):
                    rules = json.loads(rules)

                point_scale = rules.get('point_scale', {
                    'winner': 3,
                    'winner_ot': 2,
                    'loser_ot': 1,
                    'loser': 0
                })
                full_competition_data["point_scale"] = point_scale

                full_competition_data["upcoming_matches"] = upcoming_matches.to_dict('records')

                self.cache['competitions'][competition_id] = full_competition_data
                return full_competition_data
            # else:
                # print(f"Competition with id {competition_id} not found")
            # return None

    #Sauvegarde et suppression de compétition
    #########################################

    # Fonction de sauvegarde d'une compétition
    def save_competition(self, competition_id, competition_data):
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
            INSERT INTO competitions (
                competition_id, name, type, contest_mode, duration,
                predictions_method, awarding_points_method, admin_id,
                matches_data, rankings_data, duration_filter
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (competition_id) DO UPDATE SET
                name = EXCLUDED.name,
                type = EXCLUDED.type,
                contest_mode = EXCLUDED.contest_mode,
                duration = EXCLUDED.duration,
                predictions_method = EXCLUDED.predictions_method,
                awarding_points_method = EXCLUDED.awarding_points_method,
                admin_id = EXCLUDED.admin_id,
                matches_data = EXCLUDED.matches_data,
                rankings_data = EXCLUDED.rankings_data,
                duration_filter = EXCLUDED.duration_filter
            """, (
                competition_id, competition_data["name"], competition_data["type"],
                competition_data["contest_mode"], competition_data["duration"],
                competition_data["predictions_method"], competition_data["awarding_points_method"],
                competition_data["admin"], competition_data.get("matches_data", ""),
                competition_data.get("rankings_data", ""), competition_data.get("duration_filter", "")
            ))
        self.db_connection.commit()
        print(f"Saved competition: {competition_id}")

    # Fonction de suppresion d'une compétition, dans l'ExpansionPanel 'YourCompetitions'
    def remove_competition(self, instance):
        self.root.ids.competition_card.remove_widget(instance)

    #############
    # Save bets #
    #############

    def translate_to_english(self, team_name):
        translations = {
            "Suede": "Sweden",
            "Etats Unis": "USA",
            "Finlande": "Finland",
            "Canada": "Canada"
            # Add more translations as needed
        }
        return translations.get(team_name, team_name)

    def standardize_date(self, date_string):
        try:
            # Try parsing as ISO format
            return datetime.strptime(date_string, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            try:
                # Try parsing as DD/MM/YYYY format
                return datetime.strptime(date_string, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                # If both fail, return the original string
                return date_string

    def save_user_bets(self, user_email, competition_id, date, match_bets):
        if user_email not in self.sqlite_connections:
            db_path = os.path.join('user_databases', f'{user_email}_bets.db')
            self.sqlite_connections[user_email] = sqlite3.connect(db_path)

        conn = self.sqlite_connections[user_email]
        cursor = conn.cursor()

        # Ensure the bets table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id TEXT,
            match_date DATE,
            match_teams TEXT,
            bet_details TEXT,
            UNIQUE(competition_id, match_date, match_teams)
        )
        ''')
        standardized_date = self.standardize_date(date)

        # Insert or update bets
        for match, bet in match_bets.items():
            # Convert team names to English before saving
            team1, team2 = match.split(' - ')
            team1_english = self.translate_to_english(team1)
            team2_english = self.translate_to_english(team2)
            match_english = f"{team1_english} - {team2_english}"

            cursor.execute('''
                   INSERT OR REPLACE INTO bets (competition_id, match_date, match_teams, bet_details)
                   VALUES (?, ?, ?, ?)
                   ''', (competition_id, standardized_date, match_english, json.dumps(bet)))

        conn.commit()
        print(f"Saved bets for user {user_email} in competition {competition_id}")

    def load_user_bets(self, user_email, competition_id=None):
        if user_email not in self.sqlite_connections:
            db_path = os.path.join('user_databases', f'{user_email}_bets.db')
            if not os.path.exists(db_path):
                return {}
            self.sqlite_connections[user_email] = sqlite3.connect(db_path)

        conn = self.sqlite_connections[user_email]
        cursor = conn.cursor()

        if competition_id:
            cursor.execute('''
            SELECT match_date, match_teams, bet_details
            FROM bets
            WHERE competition_id = ?
            ''', (competition_id,))
        else:
            cursor.execute('SELECT competition_id, match_date, match_teams, bet_details FROM bets')

        user_bets = {}
        for row in cursor.fetchall():
            if competition_id:
                date, match, bet = row
                standardized_date = self.standardize_date(date)
                if standardized_date not in user_bets:
                    user_bets[standardized_date] = {}
                user_bets[standardized_date][match] = json.loads(bet)
            else:
                comp_id, date, match, bet = row
                standardized_date = self.standardize_date(date)
                if comp_id not in user_bets:
                    user_bets[comp_id] = {}
                if standardized_date not in user_bets[comp_id]:
                    user_bets[comp_id][standardized_date] = {}
                user_bets[comp_id][standardized_date][match] = json.loads(bet)

        return user_bets

    #############
    # Switches #
    ############

    #Fonction d'ouverture du MainScreen après entrée des informations
    def switch_to_main_screen(self):
        if not self.main_screen:
            self.main_screen = MainScreen()
        self.main_screen.load_user_data()
        self.main_screen.load_competitions()
        self.root.clear_widgets()
        self.root.add_widget(self.main_screen)
        self.main_screen.show_main_home()

    def switch_to_manage_competition_screen(self):
        self.root.clear_widgets()
        manage_competition_screen = ManageCompetitionScreen()
        self.root.add_widget(manage_competition_screen)

    def switch_to_setup_profile(self):
        self.root.clear_widgets()
        setup_profile_screen = SetupProfileScreen()
        if self.current_user:
            setup_profile_screen.ids.pseudo_field.text = self.current_user.get('pseudo', '')
            setup_profile_screen.selected_icon = self.current_user.get('icon', 'account-circle-outline')
        self.root.add_widget(setup_profile_screen)

    def switch_to_loading_screen(self):
        loading_screen = LoadingScreen()
        self.root.clear_widgets()
        self.root.add_widget(loading_screen)
        Clock.schedule_once(self.reload_data, 2)

    def reload_data(self, *args):
        self.load_all_user_competitions()
        self.switch_to_main_screen()

    def switch_to_home_screen(self):
        if not self.home_screen:
            self.home_screen = HomeScreen(name='home')
        self.root.clear_widgets()
        self.root.add_widget(self.home_screen)
        self.home_screen.on_enter()

    def switch_to_change_password_screen(self):
        change_password_screen = ChangePasswordScreen(name='change_password')
        self.root.clear_widgets()
        self.root.add_widget(change_password_screen)

    def switch_to_verification_pending_screen(self):
        verification_pending_screen = VerificationPendingScreen(name='verification_pending')
        verification_pending_screen.email = self.current_user['email']
        self.root.clear_widgets()
        self.root.add_widget(verification_pending_screen)

    def switch_to_forgot_password_screen(self):
        forgot_password_screen = ForgotPasswordScreen()
        self.root.clear_widgets()
        self.root.add_widget(forgot_password_screen)

    def switch_to_changing_screen(self, previous_screen):
        changing_screen = ChangingLanguageScreen(previous_screen_type=type(previous_screen).__name__)
        self.root.clear_widgets()
        self.root.add_widget(changing_screen)
        # Schedule the language update and screen switch
        Clock.schedule_once(lambda dt: self.perform_language_update(changing_screen.previous_screen_type), 1)

    #################
    ## Utilitaires ##
    #################

    def contact_support(self):
        support_email = "betpuckcontact@gmail.com"
        subject = "Support Request"
        body = "Please describe your issue here."

        if self.current_language == 'fr':
            subject = "Demande de support"
            body = "Veuillez décrire votre problème ici.\n\nMerci de fournir vos demandes en anglais ou en français."
        else:
            subject = "Support Request"
            body = "Please describe your issue here.\n\nPlease provide your requests in English or French."

        if platform == 'android':
            from android.intent import Intent
            intent = Intent(Intent.ACTION_SEND)
            intent.setType('message/rfc822')
            intent.putExtra(Intent.EXTRA_EMAIL, [support_email])
            intent.putExtra(Intent.EXTRA_SUBJECT, subject)
            intent.putExtra(Intent.EXTRA_TEXT, body)
            self.root.context.startActivity(intent)
        elif platform in ['ios', 'macosx']:
            url = f"mailto:{support_email}?subject={subject}&body={body}"
            webbrowser.open(url)
        else:
            url = f"mailto:{support_email}?subject={subject}&body={body}"
            webbrowser.open(url)

    #Snackbar
    #########

    # Fonction d'affichage des erreurs
    def show_snackbar(self, text):
        MDSnackbar(
            MDSnackbarText(
                text=text,
            ),
            radius=[15, 15, 15, 15],
            y=16,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
        ).open()

    def disconnect(self):
        self.current_user = None
        self.cache['competitions'].clear()
        self.cache['screens'].clear()
        self.home_screen = None
        self.switch_to_home_screen()

    def cancel_verification(self):
        self.home_screen = None
        self.switch_to_home_screen()

    def check_password_length(self, instance, text):
        max_length = 10  # You can adjust this value as needed
        if len(text) > max_length:
            instance.text = text[:max_length]
            self.show_snackbar(self.get_translation("Maximum password length of {max_length} characters reached").format(max_length=max_length))

    ########################
    ### Expansion Panels ###
    ########################

    # Fonction permettant de scroller sur les ExpansionPanel, de manière à avoir les éléments des panels en dessous
    def tap_expansion_chevron(
            self, panel: MDExpansionPanel, chevron: TrailingPressedIconButton
    ):
        Animation(
            padding=[0, dp(12), 0, dp(12)]
            if not panel.is_open
            else [0, 0, 0, 0],
            d=0.2,
        ).start(panel)
        panel.open() if not panel.is_open else panel.close()
        panel.set_chevron_down(
            chevron
        ) if not panel.is_open else panel.set_chevron_up(chevron)

    def tap_expansion_chevron_register(
            self, panel: MDExpansionPanel, chevron: TrailingPressedIconButton
    ):
        panel.open() if not panel.is_open else panel.close()
        panel.set_chevron_down(
            chevron
        ) if not panel.is_open else panel.set_chevron_up(chevron)

#############################
# Lancement de l'application
#############################

HockeyProno().run()