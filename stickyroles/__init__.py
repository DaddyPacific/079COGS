from .sticky import StickyRoles


def setup(bot):
    bot.add_cog(StickyRoles(bot))
