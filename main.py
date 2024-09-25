import requests
import telebot
import time
import random
from datetime import datetime, timedelta

# Initialize bot with token
token = input(': ')
bot = telebot.TeleBot(token)

# Dictionary to track last request time for each user
user_last_request = {}
request_limit_time = 5  # time limit in seconds for requests

# Helper function to safely make a request
def safe_request(url):
    try:
        return requests.get(url)
    except requests.exceptions.RequestException:
        return None

# Rate limiting check
def is_request_allowed(user_id):
    now = datetime.now()
    last_request_time = user_last_request.get(user_id)

    if last_request_time is None or (now - last_request_time) > timedelta(seconds=request_limit_time):
        user_last_request[user_id] = now
        return True
    return False

# Check if website has captcha
def check_captcha(url):
    response = safe_request(url)
    if response is None:
        return False
    if ('https://www.google.com/recaptcha/api' in response.text or
        'captcha' in response.text or
        'verifyRecaptchaToken' in response.text or
        'grecaptcha' in response.text or
        'www.google.com/recaptcha' in response.text):
        return True
    return False

# Check for multiple payment systems in the website
def check_credit_card_payment(url):
    response = safe_request(url)
    if response is None:
        return 'Error accessing the website'
    
    gateways = []
    if 'stripe' in response.text:
        gateways.append('Stripe')
    if 'Cybersource' in response.text:
        gateways.append('Cybersource')
    if 'paypal' in response.text:
        gateways.append('Paypal')
    if 'authorize.net' in response.text:
        gateways.append('Authorize.net')
    if 'Bluepay' in response.text:
        gateways.append('Bluepay')
    if 'Magento' in response.text:
        gateways.append('Magento')
    if 'woo' in response.text:
        gateways.append('WooCommerce')
    if 'Shopify' in response.text:
        gateways.append('Shopify')
    if 'adyen' in response.text or 'Adyen' in response.text:
        gateways.append('Adyen')
    if 'braintree' in response.text:
        gateways.append('Braintree')
    if 'square' in response.text:
        gateways.append('Square')
    if 'payflow' in response.text:
        gateways.append('Payflow')
    
    return ', '.join(gateways) if gateways else 'No recognized payment gateway found'

# Check for cloud services in the website
def check_cloud_in_website(url):
    response = safe_request(url)
    if response is None:
        return False
    if 'cloudflare' in response.text.lower():
        return True
    return False

# Check for GraphQL
def check_graphql(url):
    response = safe_request(url)
    if response is None:
        return False
    if 'graphql' in response.text.lower() or 'query {' in response.text or 'mutation {' in response.text:
        return True
    
    # Optionally, try querying the /graphql endpoint directly
    graphql_url = url.rstrip('/') + '/graphql'
    graphql_response = safe_request(graphql_url)
    if graphql_response and graphql_response.status_code == 200:
        return True
    
    return False

# Check if the path /my-account/add-payment-method/ exists
def check_auth_path(url):
    auth_path = url.rstrip('/') + '/my-account/add-payment-method/'
    response = safe_request(auth_path)
    if response is not None and response.status_code == 200:
        return 'Auth'
    return 'None'

# Get the status code
def get_status_code(url):
    response = safe_request(url)
    if response is not None:
        return response.status_code
    return 'Error'

# Check for platform (simplified)
def check_platform(url):
    response = safe_request(url)
    if response is None:
        return 'None'
    if 'wordpress' in response.text.lower():
        return 'WordPress'
    if 'shopify' in response.text.lower():
        return 'Shopify'
    return 'None'

# Check for error logs (simplified)
def check_error_logs(url):
    response = safe_request(url)
    if response is None:
        return 'None'
    if 'error' in response.text.lower() or 'exception' in response.text.lower():
        return 'Error logs found'
    return 'None'

# Generate credit card numbers based on a BIN
def generate_credit_card_numbers(bin_number):
    card_numbers = []
    for _ in range(10):  # Generate 10 card numbers
        card_number = bin_number + ''.join([str(random.randint(0, 9)) for _ in range(10)])  # Add 10 random digits to the BIN
        card_numbers.append(card_number)
    return card_numbers

# Check SK key validity
def check_sk_key(key):
    balance_response = requests.get('https://api.stripe.com/v1/balance', auth=(key, ''))
    account_response = requests.get('https://api.stripe.com/v1/account', auth=(key, ''))

    if balance_response.status_code == 200 and account_response.status_code == 200:
        account_info = account_response.json()
        balance_info = balance_response.json()

        publishable_key = account_info.get('keys', {}).get('publishable', 'Not Available')
        account_id = account_info.get('id', 'Not Available')
        charges_enabled = account_info.get('charges_enabled', 'Not Available')
        live_mode = account_info.get('livemode', 'Not Available')
        country = account_info.get('country', 'Not Available')
        currency = balance_info.get('currency', 'Not Available')
        available_balance = balance_info.get('available', [{'amount': '0'}])[0]['amount']
        pending_balance = balance_info.get('pending', [{'amount': '0'}])[0]['amount']
        payments_enabled = account_info.get('payouts_enabled', 'Not Available')
        name = account_info.get('business_name', 'Not Available')
        phone = account_info.get('support_phone', 'Not Available')
        email = account_info.get('email', 'Not Available')
        url = account_info.get('url', 'Not Available')

        # Format the response
        response = (
            f"[ϟ] 𝗦𝗞 𝗞𝗘𝗬\n{key}\n\n"
            f"[ϟ] 𝗣𝗞 𝗞𝗘𝗬\n{publishable_key}\n"
            "－－－－－－－－－－－－－－－\n"
            f"[✮] 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐃 ⬇️ [✮]\n{account_id}\n"
            "－－－－－－－－－－－－－－－\n"
            "[✮] 𝐊𝐞𝐲 𝐈𝐧𝐟𝐨 ⬇️ [✮]\n"
            f"[ϟ] 𝗖𝗵𝗮𝗿𝗴𝗲𝘀 𝗘𝗻𝗮𝗯𝗹𝗲𝗱 : {charges_enabled}\n"
            f"[ϟ] 𝗟𝗶𝘃𝗲 𝗠𝗼𝗱𝗲 : {live_mode}\n"
            f"[ϟ] 𝗣𝗮𝘆𝗺𝗲𝗻𝘁𝘀 : {payments_enabled}\n"
            f"[ϟ] 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {available_balance}\n"
            f"[ϟ] 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {pending_balance}\n"
            f"[ϟ] 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 : {currency}\n"
            f"[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝗲𝘆 : {country}\n"
            "－－－－－－－－－－－－－－－\n"
            "[✮] 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐧𝐟𝐨 ⬇️ [✮]\n"
            f"[ϟ] 𝗡𝗮𝗺𝗲 : {name}\n"
            f"[ϟ] 𝗣𝗵𝗼𝗻𝗲 : {phone}\n"
            f"[ϟ] 𝗘𝗺𝗮𝗶𝗹 : {email}\n"
            f"[ϟ] 𝗨𝗿𝗹 : {url}\n"
        )
    else:
        response = f"Invalid Key: {key}\nResponse: Invalid or expired API key ❌."

    return response

# Check single URL with /check command
@bot.message_handler(commands=['check'])
def check_url(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Please provide a valid URL after the /check command.')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, 'Please wait a few seconds before making another request.')
        return

    url = message.text.split()[1]

    try:
        captcha = check_captcha(url)
    except:
        captcha = 'Error checking captcha'

    cloud = check_cloud_in_website(url)
    payment = check_credit_card_payment(url)
    graphql = check_graphql(url)
    auth_path = check_auth_path(url)
    platform = check_platform(url)
    error_logs = check_error_logs(url)
    status_code = get_status_code(url)

    loading_message = bot.reply_to(message, '<strong>[~]-Loading... 🥸</strong>', parse_mode="HTML")
    time.sleep(1)

    # Conditionally add the 😞 emoji based on Captcha and Cloudflare detection
    captcha_emoji = "😞" if captcha else "🔥"
    cloud_emoji = "😞" if cloud else "🔥"

    # Create formatted message
    response_message = (
        "🔍 Gateways Fetched Successfully ✅\n"
        "━━━━━━━━━━━━━━\n"
        f"🔹 URL: {url}\n"
        f"🔹 Payment Gateways: {payment}\n"
        f"🔹 Captcha: {captcha} {captcha_emoji}\n"
        f"🔹 Cloudflare: {cloud} {cloud_emoji}\n"
        f"🔹 GraphQL: {graphql}\n"
        f"🔹 Auth Path: {auth_path}\n"
        f"🔹 Platform: {platform}\n"
        f"🔹 Error Logs: {error_logs}\n"
        f"🔹 Status: {status_code}\n"
        "\nBot by: @ZodMadara"
    )

    # Send the final formatted message
    bot.edit_message_text(response_message, message.chat.id, loading_message.message_id, parse_mode='html')

# Handle .txt file upload with a list of URLs
@bot.message_handler(content_types=['document'])
def handle_txt_file(message):
    file_info = bot.get_file(message.document.file_id)
    file_extension = file_info.file_path.split('.')[-1]

    if file_extension != 'txt':
        bot.reply_to(message, 'Please upload a .txt file containing URLs.')
        return

    file = bot.download_file(file_info.file_path)
    urls = file.decode('utf-8').splitlines()

    # Validate URL count (should be between 50 and 100)
    if len(urls) < 50 or len(urls) > 100:
        bot.reply_to(message, 'Please provide a .txt file with between 50 and 100 URLs.')
        return

    bot.reply_to(message, 'Processing your URLs... This may take some time.')

    # Process each URL and collect results
    results = []
    for url in urls:
        try:
            captcha = check_captcha(url)
        except:
            captcha = 'Error checking captcha'

        cloud = check_cloud_in_website(url)
        payment = check_credit_card_payment(url)
        graphql = check_graphql(url)
        auth_path = check_auth_path(url)
        platform = check_platform(url)
        error_logs = check_error_logs(url)
        status_code = get_status_code(url)

        captcha_emoji = "😞" if captcha else "🔥"
        cloud_emoji = "😞" if cloud else "🔥"

        result_message = (
            "━━━━━━━━━━━━━━\n"
            f"🔹 URL: {url}\n"
            f"🔹 Payment Gateways: {payment}\n"
            f"🔹 Captcha: {captcha} {captcha_emoji}\n"
            f"🔹 Cloudflare: {cloud} {cloud_emoji}\n"
            f"🔹 GraphQL: {graphql}\n"
            f"🔹 Auth Path: {auth_path}\n"
            f"🔹 Platform: {platform}\n"
            f"🔹 Error Logs: {error_logs}\n"
            f"🔹 Status: {status_code}\n"
        )
        
        results.append(result_message)
        time.sleep(1)  # Add a small delay between requests to avoid overloading the server

    # Send all results as a single message
    results_message = "\n".join(results)
    bot.send_message(message.chat.id, results_message, parse_mode='html')

# Generate credit card numbers command
@bot.message_handler(commands=['gen'])
def generate_cc(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Please provide a valid BIN (6-9 digits).')
        return

    bin_number = message.text.split()[1]

    if not bin_number.isdigit() or not (6 <= len(bin_number) <= 9):
        bot.reply_to(message, 'Please provide a valid numeric BIN (6-9 digits).')
        return

    card_numbers = generate_credit_card_numbers(bin_number)
    response_message = "🔍 Generated Credit Card Numbers ✅\n"
    response_message += "━━━━━━━━━━━━━━\n"
    for card in card_numbers:
        response_message += f"🔹 {card}\n"

    bot.send_message(message.chat.id, response_message, parse_mode='html')

# Check SK key command
@bot.message_handler(commands=['sk'])
def check_key(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Please provide a valid SK key.')
        return

    sk_key = message.text.split()[1]
    response_message = check_sk_key(sk_key)
    bot.send_message(message.chat.id, response_message, parse_mode='html')

# Start command handler
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        '<strong>Hello! Pro Bot for Checking Gates\n'
        'Send /check followed by the link to check the gate 🥵\n'
        'Or upload a .txt file with 50-100 URLs to check in bulk.\n'
        'Use /gen followed by a BIN to generate 10 credit card numbers.\n'
        'Use /sk followed by your secret key to check key validity.</strong>',
        parse_mode="HTML"
    )

# Help command handler
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🆘 Help - Available Commands:\n"
        "1. /start - Welcome message and bot instructions.\n"
        "2. /check <URL> - Check a specific URL for payment gateways, CAPTCHA, and more.\n"
        "3. Upload a .txt file with 50-100 URLs to check in bulk.\n"
        "4. /gen <BIN> - Generate 10 credit card numbers based on the provided BIN.\n"
        "5. /sk <SK_KEY> - Check the validity of a secret key.\n"
        "6. /help - Display this help message.\n"
        "7. /feedback - Send your feedback or report an issue.\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

# Feedback command handler
@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    bot.reply_to(message, 'Please provide your feedback or issue. I will get back to you shortly!')
    bot.register_next_step_handler(message, process_feedback)

def process_feedback(message):
    user_feedback = message.text
    # Save feedback to a file or database
    with open('feedback.txt', 'a') as f:
        f.write(f"{message.from_user.username}: {user_feedback}\n")
    bot.reply_to(message, 'Thank you for your feedback! 🙏')

# Start polling the bot
bot.polling(none_stop=True)