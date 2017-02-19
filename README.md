Seasonvar Premium
=================

Plex media plugin for http://www.seasonvar.ru. Allows you to watch TV shows and as result - waste your life...

__Requires premium subscription__ activated and a valid API key.
> See configuration section for more info.

Try Premium for free using the following link: http://seasonvar.ru/premDar.php


Current version: 1.5
--------------------

Installation
------------

1. Download git repo and place it into Plug-ins folder on your Plex media server.
> ~/Library/Application Support/Plex Media Server/Plug-ins
>> /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins/

2. New channel 'Seasonvar: Premium' should appear.

At that point the plugin is ready to be used. Next step is to configure it.

Configuration
-------------

This plugin __requires__ premium account and __will not__ work without the valid API key.

1. Find out your API key by checking [http://seasonvar.ru/?mod=api](http://seasonvar.ru/?mod=api) link.
2. Input the API key into channel preferences.
3. The last step is to activate your IP address. Run the channel and select 'Latest Serials'. As the result, you will see an error message - that's ok.
4. Navigate to [http://seasonvar.ru/?mod=api](http://seasonvar.ru/?mod=api) link and click on 'allow' for your IP address.
5. Restart the channel.

That's it. Plugin is installed and configured correctly.
