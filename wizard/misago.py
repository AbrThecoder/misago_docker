import re

from email import run_email_wizard
from utils import get_random_secret_key

FILE_HEADER = "Misago service settings"
HOSTNAME_REGEX = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
LANGUAGE_REGEX = re.compile(r"^[a-z]{2,3}(-[a-z]+)?$", re.IGNORECASE)
LANGUAGE_SEARCH_CONFIGS = {
    "en": "english",
    "nl": "dutch",
    "fi": "finnish",
    "fr": "french",
    "de": "german",
    "hu": "hungarian",
    "it": "italian",
    "no": "norwegian",
    "nb": "norwegian",
    "nn": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "es": "spanish",
    "sv": "swedish",
    "tt": "turkish",
}


def run_misago_wizard(env_file):
    # Disable debug by default, because it's safer that way
    env_file["MISAGO_DEBUG"] = "no"

    # Generate random secret key using Django's algorithm
    env_file["MISAGO_SECRET_KEY"] = get_random_secret_key()

    # Ask user to fill in some values
    run_address_wizard(env_file)
    run_language_wizard(env_file)
    run_timezone_wizard(env_file)
    run_email_wizard(env_file)

    env_file.save(FILE_HEADER)
    print("Misago configuration has been saved to %s" % env_file.path)


def run_address_wizard(env_file):
    hostname_prompt = 'Enter your site\'s hostname (eg. "mysite.com"): '
    hostname = None

    while not hostname:
        hostname = input(hostname_prompt).strip().lower()
        try:
            if not hostname:
                raise ValueError("You have to enter a hostname.")
            if len(hostname) > 255:
                raise ValueError("Hostname can't be longer than 255 characters.")
            if hostname.startswith("http"):
                raise ValueError(
                    "Hostname can't include the protocol protocol name. "
                    "Please don't include the http:// or https://."
                )
            if not all(HOSTNAME_REGEX.match(x) for x in hostname.split(".")):
                raise ValueError("Entered hostname contains disallowed characters.")
        except ValueError as e:
            hostname = None

            print(e.args[0])
            print()
            print(
                "The hostname is a domain name (optionally including the subdomain) "
                'without the protocol name (eg. "http://misago.com"), '
                'port ("misago.com:443"), '
                'or path segment ("misago.com/" or "misago.com/forum/").'
            )
            print()

    env_file["VIRTUAL_HOST"] = hostname
    env_file["MISAGO_ADDRESS"] = "https://%s" % hostname


def run_language_wizard(env_file):
    language_prompt = (
        'Enter the language code for your site\'s locale (eg. "pl" or "en-us"): '
    )
    language = None

    while not language:
        language = input(language_prompt).strip().lower().replace("_", "-")
        try:
            if not language:
                raise ValueError("You have to enter a language.")
            if not LANGUAGE_REGEX.match(language):
                raise ValueError("This is not a valid language code.")
        except ValueError as e:
            language = None
            print(e.args[0])
            print()

    env_file["MISAGO_LANGUAGE_CODE"] = language

    search_config_name = language[:2]
    if search_config_name in LANGUAGE_SEARCH_CONFIGS:
        env_file["MISAGO_SEARCH_CONFIG"] = LANGUAGE_SEARCH_CONFIGS[search_config_name]
    else:
        # fallback to "simple" config
        env_file["MISAGO_SEARCH_CONFIG"] = "simple"


def run_timezone_wizard(env_file):
    timezone_prompt = (
        "Enter the TZ Database (https://bit.ly/2glGdNY) timezone name for your site "
        '(eg. "Europe/Warsaw"): '
    )
    timezone = None

    while not timezone:
        timezone = input(timezone_prompt).strip().replace("\\", "/")
        if not timezone:
            timezone = None
            print("You have to enter a timezone name.")
            print()

    env_file["MISAGO_TIME_ZONE"] = timezone