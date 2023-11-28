import json
from nextcord.ext import commands, tasks, application_checks
from nextcord.ui import Button, View
from config import *
import nextcord
from nextcord import Permissions, PermissionOverwrite

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ticket Cog - Load')
        try:
            with open('cache.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            message_id = data.get('message_id')
        except (FileNotFoundError, json.JSONDecodeError):
            message_id = None

        channel_send = self.bot.get_channel(ticket_channel_id)
        if channel_send:
            emd = nextcord.Embed(color=0x313338)
            emd.set_image(url=img_banner)

            ticket_create = Button(style=nextcord.ButtonStyle.green,
                            label='Создать тикет',
                            emoji='📪')
            
            async def create_ticket(interaction: nextcord.Interaction):
                guild = self.bot.get_guild(guild_id)
                staff_role = interaction.guild.get_role(staff_id_role)

                category = nextcord.utils.get(guild.categories, id=category_channel_id)
                
                channel = await category.create_text_channel(name=f'ticket-{interaction.user.name}')

                user_permissions = PermissionOverwrite(read_messages=True, send_messages=True)
                role_permissions = PermissionOverwrite(read_messages=True, send_messages=True)
                everyone_permissions = PermissionOverwrite(read_messages=False, send_messages=False)

                await channel.set_permissions(interaction.user, overwrite=user_permissions)
                await channel.set_permissions(staff_role, overwrite=role_permissions)
                await channel.set_permissions(interaction.guild.default_role, overwrite=everyone_permissions)
                
                emd1 = nextcord.Embed(color=0x313338)
                emd1.set_image(url=img_banner_open_ticket)

                emd2 = nextcord.Embed(description=description_for_embed,
                                    color=0x313338)
                emd2.set_image(url=line)
                
                async def create_ticket(interaction: nextcord.Interaction):
                    user = interaction.user
                    if staff_role in user.roles:
                        await channel.delete()
                    else:
                        embed = nextcord.Embed(description='Вы не можите закрыть тикет! Закрывать тикет могут только стафф',
                                            color=0x313338)
                        await interaction.response.send_message(embed=embed, ephemeral=True)

                ticket_close = Button(style=nextcord.ButtonStyle.red,
                            label='Закрыть',
                            emoji='🔒')
                
                ticket_close.callback = create_ticket
                view = View(timeout=None)
                view.add_item(ticket_close)

                ms1 = await channel.send(f'<@&{staff_id_role}>', embeds=[emd1, emd2], view=view)
                await ms1.pin()
                
            ticket_create.callback = create_ticket
            view = View(timeout=None)
            view.add_item(ticket_create)

            if message_id is None:
                message_ch = await channel_send.send(embed=emd, view=view)
                data = {"message_id": message_ch.id}

                with open('cache.json', 'w') as json_file:
                    json.dump(data, json_file)
            else:
                message_ch = await channel_send.fetch_message(message_id)
                await message_ch.edit(embed=emd, view=view)

def setup(bot):
    bot.add_cog(Ticket(bot))
