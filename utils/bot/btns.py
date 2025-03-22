from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from .btn_texts import *


def accept_send_btns(lang='ru', user_id='', send_id=''):
    keyb = InlineKeyboardMarkup()
    btn_accept = InlineKeyboardButton(confirmation_texts.get('confirm', {}).get(lang), callback_data=f"confirm_send_{user_id}_{send_id}")
    btn_deny = InlineKeyboardButton(confirmation_texts.get('deny', {}).get(lang), callback_data=f"deny_send_{user_id}_{send_id}")
    keyb.add(btn_accept, btn_deny)
    return keyb


def accept_withdraw_btns(lang='ru', user_id='', withdraw_id=''):
    keyb = InlineKeyboardMarkup()
    btn_accept = InlineKeyboardButton(confirmation_texts.get('confirm', {}).get(lang), callback_data=f"confirm_withdraw_{user_id}_{withdraw_id}")
    btn_deny = InlineKeyboardButton(confirmation_texts.get('deny', {}).get(lang), callback_data=f"deny_withdraw_{user_id}_{withdraw_id}")
    keyb.add(btn_accept, btn_deny)
    return keyb


def accept_balance_btns(lang='ru', user_id='', balance_id=''):
    keyb = InlineKeyboardMarkup()
    btn_accept = InlineKeyboardButton(confirmation_texts.get('confirm', {}).get(lang), callback_data=f"confirm_balance_{user_id}_{balance_id}")
    btn_deny = InlineKeyboardButton(confirmation_texts.get('deny', {}).get(lang), callback_data=f"deny_balance_{user_id}_{balance_id}")
    keyb.add(btn_accept, btn_deny)
    return keyb


def accepted_btns(lang='ru'):
    keyb = InlineKeyboardMarkup()
    btn_accepted = InlineKeyboardButton(accepted_text.get(lang), callback_data=f"already_accepted")
    keyb.add(btn_accepted)
    return keyb


def denied_btns(lang='ru'):
    keyb = InlineKeyboardMarkup()
    btn_denied = InlineKeyboardButton(denied_text.get(lang), callback_data=f"already_denied")
    keyb.add(btn_denied)
    return keyb
