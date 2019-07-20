# LIBRARY IMPORTS

import re
import time

# THIRD PARTY IMPORTS

import discord
from discord.ext import commands

# PROJECT IMPORTS

import utilities.vqueries as vquery
import utilities.catalogue as catalogue

# CONSTANTS



#

class Courses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def coursealias(self, ctx, *args):
        """
            creates an alias - aliases must be a single word

            coursealias <alias> <department>
        """
        if len(args) != 2:
            await ctx.send(f'**{ctx.message.content}**\nIncorrect format, please use `$courseinfo <department> <alias>`\nIf your arg contains a space please put it in quotes, "de part ment"')
        else:
            department = args[0].upper()
            alias = args[1].upper()
        try:
            await vquery.insert_catalogue_alias(self.bot.pool, department, alias, ctx.guild.id)
            await ctx.send(f'**ALIAS CREATE**\nAlias -> {department}\nDepartment -> {alias}')
        except Exception as e:
            await ctx.send(f'Bot Brok {e}')
        else:
            self.bot.aliases[alias] = department

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def removealias(self, ctx, department):
        """
            removes an alias from the bot

            USAGE: removealias <alias> 
        """
        try:
            department = department.upper()
            if department in self.bot.aliases:
                await vquery.remove_catalogue_alias(self.bot.pool, department.upper(), ctx.guild.id)
                del self.bot.aliases[department]
                await ctx.send(f'{department} removed from aliases')
            else:
                await ctx.send(f'{department} alias does not exist, make sure you are removing the alias and not the department')
        except Exception as e:
            await ctx.send(f'Bot Brok {e}')
        

    # @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def aliases(self, ctx):
        """
            gets all the aliases registered with the bot

            USAGE: getaliases
        """
        embed = discord.Embed(title='Course Aliases')
        for key, value in (await vquery.request_catalogue_aliases(self.bot.pool)).items():
            embed.add_field(name=f'Department = {value}', value=f'Alias = {key}', inline=False)
        await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.command()
    async def courseinfo(self, ctx, *args):
        """
            gets the information specified for a course in the UCI Catalogue

            USAGE: courseinfo <DEPARTMENT ID>

            Example: courseinfo ENGRCEE 81B
        """
        try:
            start = time.time()
            department = (' '.join( args[:len(args) - 1] )).upper()
            if department in self.bot.aliases:
                department = self.bot.aliases[department]
            course = await self.bot.courses.get_course(' '.join([department, args[len(args) - 1]]))
            end = time.time()
        except Exception as e:
            await ctx.send(f'Bot Brok {e}')
        else:
            with ctx.typing():
                embed = discord.Embed(title=f'**{course.course_title}**', description=f'**{course.course_id}** - *{course.course_units}*', color=1938213)
                embed.add_field(name='Course Description', value=course.course_desc, inline=False)

                if course.prereqs is not None:
                    embed.add_field(name='Requisites', value=course.prereqs, inline=False)
                if course.restrictions is not None:
                    embed.add_field(name='Restrictions', value=course.restrictions.rstrip('Restrictions'))
                if course.overlaps is not None:
                    embed.add_field(name='Course Overlaps', value=course.overlap, inline=False)
                if course.concurrent is not None:
                    embed.add_field(name='Course Concurrent', value=course.concurrent, inline=False)
                if course.same_as is not None:
                    embed.add_field(name='Same Course', value=course.same_as, inline=False)
                if course.grading_option is not None:
                    embed.add_field(name='Grading Options', value=course.grading_option, inline=False)
                if course.repeatability is not None:
                    embed.add_field(name='Repeatability', value=course.repeatability, inline=False)
                if course.spillover != []:
                    embed.add_field(name='Not Implemented', value=course.spillover, inline=False)
                embed.add_field(name='Processing Time', value=str(end-start), inline=False)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def getdepartments(self, ctx, letter):
        """
            Gets all the departments by a letter

            USAGE: getdepartments <letter>
        """
        try:
            embed = discord.Embed(title=f'**Course Tags for - {letter.upper()}**', description='\n'.join( await self.bot.courses.get_departments( letter.upper() ) ), color=1938213)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f'getdepartments requires a given letter\nExample: getdepartments A')


def setup(bot):
    bot.add_cog(Courses(bot))


