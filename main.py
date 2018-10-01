import discord, os, random
from db_utils import *
from discord.ext import commands
from forex_python.converter import CurrencyRates

bot = commands.Bot(command_prefix='umi.')
bot.remove_command('help')
db = sqlite3.connect('umikobot.db')

currencies = CurrencyRates().get_rates('NOK')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('DISCORD {} CONNECTION ESTABLISHED'.format(discord.__version__))
    print('------')
    await bot.change_presence(activity=discord.Game(name='umi.help'))


@bot.command()
async def help(ctx):
    r_string = '```Markdown\nWelcome to UmikoBot, a rewrite of AusCha\'s NeneBot using Discord 1.0.0a!' + \
               '\n\nUmiko works by scanning your entire message for keywords.' + \
               '\n\nYou will find all recognised input below:' + \
               '\n\n<i.[tag]>: Image macros, and must be the first word in your message. ' + \
               'Add a command with <umi.addimage [tag] [url]>, and see the full list with <umi.images>!' + \
               '\n\n<umi.ccyconvert [amount] [ccy_pair]>: Currency conversion from first currency to second. Not to be used for trading.' + \
               '\n\nUmiko also has other useless functionality, as she is an academic exercise for AusChA\'s interview prep.```'
    await ctx.send(r_string)


@bot.command()
async def info(ctx):
    embed = discord.Embed(title="UmikoBot", description="A rewrite of AusChA\'s NeneBot using Discord 1.0.0!")
    embed.add_field(name="Author", value="AusChA#0474")
    await ctx.send(embed=embed)


@bot.command()
async def images(ctx):
    embed = discord.Embed(title="Image List", description="All image macros accessible via i.<tag>.")
    embed.add_field(name="Tags", value='\n'.join(get_keys('Images')))
    await ctx.send(embed=embed)


@bot.command()
async def addimage(ctx, key: str, url: str):
    if key in get_keys('Images'):
        await ctx.send('Tag already in use. Please change image tag and try again.')
    elif url.startswith('http'):
        await ctx.send(db_add('Images', key, url))
    else:
        await ctx.send('URL not recognised. Please try again.')


@bot.command()
async def removeimage(ctx, key: str):
    if key in get_keys('Images'):
        await ctx.send(db_delete('Images', key))
    else:
        await ctx.send('Tag not in use. Nothing deleted.')


@bot.command()
async def ccyconvert(ctx, amount: float, ccy_pair: str):
    ccy_pair = ccy_pair.upper()

    if len(ccy_pair) == 6:
        cr = CurrencyRates()
        rate = cr.get_rates(ccy_pair[3:])[ccy_pair[:3]]

        await ctx.send(
            '```{} {} is {} {}.```'.format(ccy_pair[:3], round(amount, 2), ccy_pair[3:], round((amount * 1 / rate), 2)))


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    else:
        await bot.process_commands(message)

        # Image macros
        if message.content.split(' ')[0].startswith('i.'):
            await message.channel.send(db_retrieve('Images', message.content.lower().split(' ')[0].split('.')[1]))

        # Translations
        for s in message.content.lower().split(' '):
            if s in get_keys('Translations'):
                await message.channel.send(db_retrieve('Translations', s))

        # Ayy and eyy
        yy_words = [word for word in message.content.lower().split(' ') if
                    word.endswith('yy')]

        if 'ahagon' in message.content.lower():
            await message.channel.send(random.choice([
                                                        'Don\'t call me by my surname... I\'ve always told you! :gun:',
                                                        'Please call me U-mi-ko. Are we clear?',
                                                        'Please stop calling me that.',
                                                        'How many times must I tell you that it\'s "Umiko"?',
                                                        'https: // i.imgur.com / S1mDMaf.jpg',
                                                    ]))

        if '阿波根' in message.content or 'あはごん' in message.content or 'アハゴン' in message.content:
            await message.channel.send('名字で呼ぶなと。。。いつも言ってるでしょ！ :gun:')

        if message.content.lower().startswith('tadaima'):
            await message.channel.send('Okaeri!～')

        if message.content.startswith('ただいま'):
            await message.channel.send('お帰りなさい。')

        if len(yy_words) > 0 and yy_words[0].startswith('ayy'):
            await message.channel.send(ayyifier(len(yy_words[0]) - 3, 'lmao', 'o', ''))
        elif len(yy_words) > 0 and yy_words[0].startswith('eyy'):
            await message.channel.send(ayyifier(len(yy_words[0]) - 3, 'ellmao', 'o', 'w'))

        if message.content.lower() == 'noice':
            await message.channel.send('ikr')

        if message.content.lower().startswith('sa') and message.content.lower().endswith(
                'ame') and ' ' not in message.content.lower():
            await message.channel.send(ayyifier(len(message.content) - 4, 'sa', 'a', 'ame'))

        if any(ccy in message.content.upper() for ccy in currencies.keys()) or any(
                ccy in message.content for ccy in ['$', '€', '£', '円', '¥']):
            await message.channel.send(norway_fx(message.content.upper()))


def norway_fx(message):
    message = message.replace('$', 'AUD')
    message = message.replace('€', 'EUR')
    message = message.replace('£', 'GBP')
    message = message.replace('円', 'JPY')
    message = message.replace('¥', 'JPY')
    message = message.replace('dollar', 'AUD')
    message = message.replace('euro', 'EUR')
    message = message.replace('pound', 'GBP')
    message = message.replace('yen', 'JPY')
    message = message.replace('yuan', 'NTD')
    for ccy in currencies.keys():
        if ccy in message:
            message_list = message.split(ccy)
            preceding = [s for s in message_list[0].split(' ') if s is not ''][-1] if message_list[0] else None
            following = [s for s in message_list[1].split(' ') if s is not ''][0] if message_list[1] else None

            if is_float(following):
                value = following
            elif is_float(preceding):
                value = preceding
            else:
                continue
            return '```T/N: {} {} is {} Norwegian Krone.```'.format(ccy, round(float(value), 2),
                                                                    round(float(value) * 1 / currencies[ccy], 2))


def is_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def ayyifier(repeat_count, start, repeater, end):
    return start + (repeat_count * repeater) + end


bot.run(os.environ['DISCORD_BOT_TOKEN'], reconnect=True)
