# AutoUnsub

A python tool that scans your gmail inbox for senders with unsubscribe options and lets you unsubscribe from them without opening a bunch of emails yourself.

## Overview

I made AutoUnsub because my inbox was getting kinda stupid with newsletters random notifications and stuff I signed up for once and completely forgot about.

Unsubscribing isnt really hard but doing it over and over again is annoying so i wanted to just automate that part, so

it uses gmail IMAP to scan message headers and a small parser to figure out what unsubscribe option an email has.  SQLite keeps track of the senders and messages so the same stuff doesnt keep getting counted

i also didnt wanna put everything into one massive python file so `main.py` is the only thing you actually run and everything else is split into smaller files.

<img width="1253" height="925" alt="image" src="https://github.com/user-attachments/assets/aa750961-83e9-48cc-bd40-a28c8f3c5c42" />


## Features

| Feature                                               |
| ----------------------------------------------------- |
| Scan Gmail from however many days back you want       |
| Set a max number of messages to scan                  |
| Detect one click unsubscribe options                  |
| Detect normal HTTP and HTTPS unsubscribe links        |
| Detect `mailto:` unsubscribe links                    |
| Store senders and message data in SQLite              |
| Dont count the same message twice                     |
| Show message counts for each sender                   |
| Show unsubscribe methods                              |
| Unsubscribe from one sender                           |
| Unsubscribe from multiple senders                     |
| Track successful and failed attempts                  |
| Store the Gmail app password using the system keyring |
| Colored terminal interface                            |

<img width="1441" height="851" alt="image" src="https://github.com/user-attachments/assets/40babdb4-8bb8-497a-b073-03e4296dbc99" />


## How It Works

`Gmail -> IMAP -> parser -> SQLite -> terminal -> unsubscribe`

the scanner only gets the headers it actually needs instead of downloading the whole email

then it pulls out the sender date and unsubscribe info and sends that into the parser after which

the results get stored in SQLite so AutoUnsub remembers what it has already seen, and

when you unsubscribe it uses whatever method was found in the email.

One click options use a POST request,normal links use an HTTP request and `mailto:` options get turned into an email and sent through Gmail SMTP

## Project Structure

| Path                     | Contents                                 |
| ------------------------ | ---------------------------------------- |
| `main.py`                | the thing you actually run               |
| `sweeper/config.py`      | handles Gmail credentials                |
| `sweeper/db.py`          | DB                                       |
| `sweeper/imap_scan.py`   | scans gmail                              |
| `sweeper/sweep.py`       | connects the scanner parser and database |
| `sweeper/unsub_parse.py` | figures out unsubscribe methods          |
| `sweeper/unsubscribe.py` | actually sends the unsubscribe request   |
| `tests/`                 | tests for everything                     |
| `requirements.txt`       | python dependencies                      |
| `README.md`              | this file                                |

## Install

### From PyPI

Once released, the normal user install is:

```bash
python -m pip install auto-unsub
auto-unsub
```

This installs AutoUnsub as a real command-line application, so users do not need to clone the repository.

### From source

For development:

```bash
python -m pip install -e .
auto-unsub
```


on the first run it asks for your gmail address and app password

the app password gets stored using the system keyring so you dont have to enter it every time

you do have to make the app password yourself from your google account first tho

<img width="636" height="349" alt="image" src="https://github.com/user-attachments/assets/ead0f025-be57-4020-8a56-6d1465b6fa4b" />


after that you choose how many days back you wanna scan and how many messages you wanna check

then it shows you what it found

<img width="569" height="298" alt="image" src="https://github.com/user-attachments/assets/51aeb6e0-1397-44e1-b909-264d8b6d9218" />


## What I Learned

honestly this taught me way more than i expected

I learned how Gmail IMAP works and how email headers are structured and how unsubscribe headers can have a bunch of different formats,

also I got way more comfortable with SQLite and keeping state between runs.

The networking part was kinda interesting too because fetching messages one by one was ridiculously slow so i changed it to fetch them in batches(default 25 but i can change this)

Real email data was also way messier than the fake tests i started with cuz some emails have no unsubscribe options at all and some have huge weird unsubscribe urls.

## Why I Built It

mostly because i wanted it for myself

<img width="1631" height="722" alt="image" src="https://github.com/user-attachments/assets/7caeb23b-b4fb-4604-ad5d-55b24db723ad" />


my inbox has a bunch of random stuff that i dont really care about anymore and manually cleaning it up is just boring, and repetitive.

## Current Status

The main thing works now

AutoUnsub can connect to Gmail scan real messages, figure out which ones have unsubscribe options, save everything to SQLite and actually send unsubscribe requests.

the interface is still pretty basic and theres still a lot i wanna improve, which is

mainly making the scanning less slow, handling weird unsubscribe services better and making the whole thing feel like an actual finished app.
