import asyncio
import discord
from discord.ext import commands

class SongEntry:
    """ Placeholder class for now playing song formatting. """
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

class VoiceState:
    """ Defines the methods for interacting with the current voice state. """
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        """ Returns boolean if playing """
        if self.current is None:
            return False
        player = self.current.player
        return not player.is_done()

    def skip(self):
        """ Skips current song. """
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        """ Fastforwards to next song """
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self, ctx):
        """ Looped task performing all song functions. """
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            now_playing = 'Now playing ' + str(self.current.player.title)
            await self.bot.send_message(self.current.channel, now_playing)
            self.current.player.start()
            await self.play_next_song.wait()

    @property
    def player(self):
        """ Returns the player """
        return self.current.player

class Voice(commands.Cog):
    """Voice related commands."""
    def __init__(self, bot):
        self.bot = bot
        self.state = {}

    def get_voice_state(self, server):
        state = self.state.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.state[server.id] = state
        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, *, channel: discord.VoiceChannel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await ctx.message.channel.send('Already in a voice channel...')
        else:
            await ctx.message.channel.send('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await ctx.message.channel.send('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)
        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str):
        """ Plays a youtube url, radio url, or song from query. """
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }
        state = self.get_voice_state(ctx.message.server)

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return
        try:
            player = await state.voice.create_ytdl_player(
                song,
                ytdl_options=opts,
                after=state.toggle_next
                )
        except Exception as err:
            print('[!!] Error: ' + err.__cause__)
        else:
            player.volume = 0.25
            entry = SongEntry(ctx.message, player)
            await ctx.message.channel.send('Added ' + player.title)
            await state.songs.put(entry)
    @commands.command(pass_context=True, no_pm=True)
    async def radio(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return
        try:
            player = await state.voice.create_ytdl_player("http://shinsen-radio.org:8000/shinsen-radio.128.ogg")
        except Exception as err:
            print('[!!] Error: ' + str(err))
        else:
            player.volume = 0.25
            await ctx.message.channel.send('Playing radio')
        
    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """ Skips currently playing song. """
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await ctx.message.channel.send('Not playing anything...')
            return
        state.skip()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """ Stops currently playing music. """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.state[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        """ Set the volume of the current song. """
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await ctx.message.channel.send('Volume set to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """ Pause the currently playing song, or radio. """
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """ Resume the currently playing song, or radio. """
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
