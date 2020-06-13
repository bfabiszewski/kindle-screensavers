Hi :)

You'll find here the FW 5.x (KT/PW/PW2/KT2/KV/PW3/KOA/KT3/KOA2/PW4) port of the ScreenSavers : http://www.mobileread.com/forums/showthread.php?t=88004 hack, along with a Python 2.7.15 package ;).

*What Does It Do?:*

This will allow you to customize the screensavers (or sleep screens) used by your Kindle, replacing them either with your choice of images, the cover of the last book you opened or a simple unobtrusive overlay ;).



*Latest Updates (06/04/2019):*

ScreenSavers v0.25.N (Minor bugfixes, updated binaries), Python v0.15.N (Updated binaries, Python 2.7.16).

*PSA:* All downloads have been moved to the Snapshots : https://www.mobileread.com/forums/showthread.php?t=225030 thread!



*IMPORTANT NOTE REGARDING UPDATES:*

Here are general *update* instructions for these hacks:

    * No need to run the Update_*_uninstall.bin updates, ever.
    * You simply have to apply the latest Update_*_install.bin updates, one by one (or all at once when using MRPI : http://www.mobileread.com/forums/showthread.php?t=251143).



*INSTALL:*

*ScreenSavers:*


*Note for Kindle Special Offers Users:*

This doesn't, and won't ever, help you bypass something you agreed to (screensaver ads), so please stop asking.

If you still have questions, please read this post : http://www.mobileread.com/forums/showthread.php?t=200942.

That said, you can unsubscribe to Special Offers at any point of the process with no ill effect.
Do note that the "Swipe to Unlock" behavior is a particularity of the Special Offers screensavers that this hack will not replicate (this is in particular good to know if you happen to own a magnetic cover, since those severely limit the effective amount of time you'll actually _see_ a screensaver).



First of all, make sure your device is JailBroken : http://www.mobileread.com/forums/showthread.php?t=186645.

*If you intend to use the *cover* feature:*

It will use the cover of the last book opened as the current screensaver.
Be aware that you'll need > 150MB of free space on your device for the install to proceed.
Download the _K5_ *Python* package from the Snapshots : https://www.mobileread.com/forums/showthread.php?t=225030 thread, and unpack it. In here, you'll find a few files.
If you own a PW2 or a Kindle Basic, use the kindle-python-0.15.N-pw2_kt2_kv_pw3_koa_kt3_koa2_pw4_kt4.zip file, or if you own a Touch or a PW1, use the kindle-python-0.15.N-touch_pw1.zip file.

First, upload the appropriate install .bin file for your device (*Update_python_0.15.N_install_pw2_kt2_kv_pw3_koa_kt3_koa2_pw4_kt4.bin* for a PW2 or a KT2 or a KV or a PW3 or a KOA or a KT3 or a KOA2 or a PW4 or a KT4, the other one for a Touch or a PW1) to the _mrpackages_ directory of your Kindle.

As we're using MRPI, we can leave it here and go on with the main hack, both will be installed at the same time, and in the right order ;).



As usual, you'll need MRPI : https://www.mobileread.com/forums/showthread.php?t=251143 for the install process.

Download the _K5_ *ScreenSavers Hack* package from the Snapshots : https://www.mobileread.com/forums/showthread.php?t=225030 thread, and unpack it. In here, you'll find a few files.

First, upload the appropriate install .bin file for your device (*Update_linkss_0.25.N_install_pw2_kt2_kv_pw3_koa_kt3_koa2_pw4_kt4.bin* for a PW2 or a KT2 or a KV or a PW3 or a KOA or a KT3 or a KOA2 or a PW4 or a KT4, the other one for a Touch or a PW1) to the _mrpackages_ directory of your Kindle.

Now, eject & unplug your Kindle, and and run MRPI via KUAL: *Helper -> Install MR Packages*. It should take a couple dozen of seconds.

Note that if you have KUAL : http://www.mobileread.com/forums/showthread.php?t=203326 set up and running, you're welcome to use our very own MR Package Installer : http://www.mobileread.com/forums/showthread.php?t=251143, which may speed up the process if you're installing multiple things ;).

Once your device has finished rebooting, check that everything went fine by putting your Kindle to sleep: on a fresh install, you should now see a special screensaver to confirm that the installation was successful ;). Carry on if you do, otherwise, check the FAQ at the bottom of this message.

You now have a couple of choices to make:

Do you want to use the cover of the last book opened as a screensaver? Make sure you've installed the Python package first, then just drop a blank file named *cover* in the linkss folder. Restart your Kindle (*[HOME] -> [MENU] > Settings -> [MENU] > Restart*; or simply use the *Screen Savers* > *Restart framework now* button in KUAL), and you're done :).

Dou you prefer to just show the last thing that was on screen, with an overlay indicating when the device's alseep? Just drop a blank file named *last* in the linkss folder. Restart your Kindle (*[HOME] -> [MENU] > Settings -> [MENU] > Restart*; or simply use the *Screen Savers* > *Restart framework now* button in KUAL), and you're done :).

A couple of things to note on these two modes: the cover mode will always take precedence (so, yeah, enabling both last & cover really doesn't make much sense).
The autoreboot feature is probably useless to you in these two modes, so you should also delete the *autoreboot* file in the linkss folder if you still have autoreboot enabled.

If you simply want to use a set of custom screensavers, like usual, keep on reading :).

To change your custom screensavers, plug your Kindle to your computer via USB, and upload them to the *linkss/screensavers* folder that has been created by the hack. You'll *have* to restart your Kindle in order to take your new screensavers into account and prevent the framework from going crazy. To that effect, you can either use the framework restart KUAL button, the autoreboot feature, or simply do a full restart of your Kindle.

A small reminder of the file format & size you *have* to use:
One the Touch/KT2/KT3: PNG files, 600x800. Grayscale if possible, but color works too (you can even play with an alpha channel if you like).
One the PW/PW2: PNG files, 758x1024. Grayscale if possible, but color works too (you can even play with an alpha channel if you like).
One the KV/PW3/KOA: PNG files, 1072x1448. Grayscale if possible, but color works too (you can even play with an alpha channel if you like).
You *NEED* to follow these directives: non-PNG files will be discarded by the hack, and broken files or files in the wrong resolution will confuse the framework and trigger weird issues.

To use the autoreboot feature: Once it's enabled & active, just drop a blank file named *reboot* in the linkss folder (by copying and renaming the already existing "autoreboot" blank file, for example), and your Kindle will do a quick reboot 10s after you've unplugged it (there's minimal visual feedback during that time, just wait until your list of books reappear)!

If you want to randomize the sequence in which your screensavers will be shown, create a blank file named *random* in the linkss folder (right alongside the "auto" file), and then restart your Kindle (or, again, simply the framework through KUAL)! This will shuffle your screensavers around on each boot.

In addition to this, you can also shuffle your screensavers each time a framework restart is triggered through the autoreboot feature. Be advised that this may significantly (a few dozen of seconds) delay the framework restart procedure, depending on the number of screensavers you're using. To enable this feature, create a blank file named *shuffle* in the linkss folder (right alongside the "auto" file), and then restart your Kindle (either through the framework restart KUAL button, the autoreboot feature, or a full restart).

*Since v0.8.N:* All of these settings are now available in a friendly *KUAL* : http://www.mobileread.com/forums/showthread.php?t=203326 menu :). Running at least KUAL 2.1 is recommended for the best user experience. On the PW2, you'll need KUAL 2.3 (barring that, a recent enough snapshot : http://www.mobileread.com/forums/showthread.php?t=225030).


*Since v0.7.N:* Cover mode now has an extra "Personal Information" feature:

This will overlay a personalized banner at the bottom of the current cover. This banner is intended to contain contact information, information which is pulled from the personal information entered in your Kindle's settings.
This feature can be enabled by dropping a blank file named *pinfo* in the linkss folder, or by relying on the relevant KUAL button in the Cover Mode settings.
The actual text displayed at the bottom of the screensaver is by default prepended by a hardcoded "_If found, please contact: _" string, but if you put your own string in a file named *pinfo_header* in the linkss folder, then the content of that file will be used instead. Note that in both cases, the gist of the info will still come from the Kindle's proper personal info settings.
Note also that carriage returns are converted to semi-colons to avoid layout issues.

Once generated, much like the covers, that banner is cached, so if you ever change your personal info or the header, you'll have to wipe said cache. A couple buttons in KUAL are designed specifically for this :).


*NOTES & TROUBLESHOOTING:*

Don't try to force a custom update by rebooting your Kindle. You should *always* install custom hacks via the Settings page. If the 'Update Your Kindle' link is greyed out, you did something wrong, or you have an unknown Kindle model (in which case, contact me!). Don't try to force an install by rebooting. It'll, at best, fail.

If the cover mode seems to be behaving strangely, make sure the date and time is properly set on your device (check that, when sorting your Home screen by 'Recent', you get consistent & accurate results) and that the books you're using actually have a cover properly tagged & embedded. One other thing to keep in mind is that the switch is not done immediately on the opening of a book, but only a few seconds later, and that, when opening a book for the first time, the parsing & processing of the cover can take a noticeable amount of time (usually between 30s and a minute, depending on the CPU load).

In the classic 'image cycle' mode, if your Kindle simply goes to sleep on the last thing shown on the screen (the light going dark on the PW is a good indication that the device is asleep), it most likely means one of your custom images is broken (wrong format, weird encoding issue, weird size issue, or any number of fun & interesting ways to make the Kindle unhappy). Once you've identified the file(s) causing the issue, remove them from the screensaver folder, and restart your device (or simply the framework through KUAL).

If the cover processing seems to take an inordinate amount of time (>30s), try to go back to the Home screen for a while after opening a new book, and/or consider enabling the *lowmem* mode.

Another thing: every time I mention rebooting or restarting your device, you need to do it with the device completely *unplugged*. It may sound weird, but it affects a number of things in weird and interesting ways ;).


*FAQs:*

Here's list of the most common issues & their cause, as a kind of self-diagnostic you can do yourself to see if you missed something ;).

* In *cycle* mode (ie. not cover or last):

*Q*. Got the SO screensavers?
*A*. Tough luck, it's an SO device, unsubscribe (See the 'Manage Your Devices' section in the 'Manage Your Kindle' page @ Amazon) ;).

*Q*. Got the default screensavers?
*A*. The install failed (which should be easy to catch during the install process itself), or the hack disabled itself for some reason (that should trigger a warning at the bottom of the screen, and in cycle mode, that's usually because the screensavers folder is empty, or was emptied by the hack because none of the stuff in it remotely looked like a valid image file (on FW 5.x, that means a png file, lowercase).

If you think you did things correctly, and yet still get the default screensavers, check the fourth answer below: make sure you don't boot your device while it's plugged to something.

*Q*. Get the default 'Hi, I'm the screensavers hack' screen?
*A*. There are no custom files in your linkss/screensavers folder :).

*Q*. Get the last thing shown on screen (or a blank screen on FW 2/3/4) in cycle mode, either straight-away or after a few working custom images?
*A*. One of the files in your screensaver pool upset the Kindle firmware ;). That rarely happens on FW 2/3/4 (you're much more likely to see a corrupted image, rather than breaking the whole thing, which is what happens on FW 5.x: once it fails in this way, only a reboot will make the framework try again, even if the next file in the cycle is okay, the framework just appears to give up on screensavers), but on FW 5.x, that means checking the size, format, resolution of each and every file in your pool, to see if it matches the device, and really is a PNG8 (256c) (optionally properly dithered down to 16 colors, but _not_ indexed to 16c), without any embedded ICC profile.

Another likely way to trigger that issue is to boot (which also means restart, which is what happens right at the end of an update on FW 5.x) while the device is plugged to something (especially a computer: a wall charger _should_ be fine, but just in case…) ;). I'm guessing this also impacts the *last* mode, but the *cover* mode _should_ be fine (although you're still exposing yourself to all the vanilla things that can go wrong when you boot a Kindle like this ;)).
TL;DR: Unplug your device.

* Optionally, in *shuffled* cycle mode, if something specifically breaks after an autoreboot, it means I messed up ;).

* In *last* mode:

  It's so simple that I can't think of anything wrong ever happening ^^.

* In *cover* mode:

*Q*. Get the default 'Hi, I'm the ScreenSavers Hack, I'm in cover mode'?
*A*. Either you didn't wait long enough after opening a new book before letting the Kindle sleep, or the book format isn't supported (PDF, Topaz (+ dictionaries on FW 5.x)), or the book doesn't have a cover properly flagged in its metadata (might happen with some weird, old prc files, haven't really checked), in which case a warning is triggered on screen (in verbose mode).

*Q*. Get the cover of the next to last book you opened, not the last?
*A*. Same answer as before :). (On FW 2/3/4, that might still happen for the first sleep cycle after a book switch, there's an (ugly) workaround available in the settings for that). On FW >= 5.6.5, be aware that the processing of KFX books is highly experimental ;).

*Q*. Get the cover of a seemingly random book?
*A*. Check that the date/time on your device is sane ;). On FW >= 5.6.5, be aware that the processing of KFX books is highly experimental ;).

*Q*. I want truly dynamic screensavers, even when the device is asleep!
*A*. Then take a look at this : http://www.mobileread.com/forums/showthread.php?t=236104 :)!



*ChangeLog:*


**ScreenSavers*:

    * *v0.1.N*:
    
        * First release :).
    
    * *v0.2.N*:
    
        * Some more safety checks to disable the hack in case we can't use any of the screensavers provided by the user
        * Drop a specific file to help third-party tools ID the Kindle model
        * Enable the autoreboot feature by default
        * Implement a new setting: use the cover of the last book opened as the screensaver! (Drop a blank *cover* file in the linkss folder to enable this mode)
        * Implement a new setting: use the last page/menu shown as the screensaver (with a minimal overlay indicating that the device is asleep). (Drop a blank *last* file in the linkss folder to enable this mode)
    
    * *v0.3.N*:
    
        * Fix a few minor bugs
        * Allow users to choose not to conserve aspect ratio when in cover mode (Drop a blank *stretch* file in the linkss folder)
    
    * *v0.4.N*:
    
        * Resync our trimmed down Mobi Unpack stuff with v0.59
    
    * *v0.5.N*:
    
        * Updated binaries (updated tc, coreutils)
    
    * *v0.6.N*:
    
        * Tweak the processing settings in cover mode to generate higher quality images (sharper upscaling algo, better dithering).
    
    * *v0.7.N*:
    
        * Tweak the processing settings in cover mode to generate smaller files.
        * Implement a new cover mode setting: black letterboxing borders. (Drop a blank *black* file in the linkss folder to enable this mode)
        * Implement a new cover mode setting: a small banner with your personal infos at the bottom of the screen. (Drop a blank *pinfo* file in the linkss folder to enable this mode)
        * Implement a new cover mode setting: automatically crop the borders, to end up with a full screen cover. (Drop a blank *autocrop* file in the linkss folder to enable this mode)
        * Experimental support for overriding FW 5.3's custom screensavers (Drop a blank *beta* file in the linkss folder)
        * Updated binaries (updated tc, coreutils)
    
    * *v0.8.N*:
    
        * New KUAL extension (at the time of release, requires the development version of KUAL)
        * Tweaked the processing settings a bit to play nice with the new ImageMagick build. Possibly a bit faster.
        * Updated binaries (updated tc, everything)
    
    * *v0.9.N*:
    
        * Made the default & fallback image in cover mode a bit more helpful than a blank screen ;).
    
    * *v0.10.N*:
    
        * Tweaked the KUAL menu a bit.
        * Optimized cover & last mode behavior, IO wise.
    
    * *v0.11.N*:
    
        * Updated binaries (updated tc)
        * Tweaked how the cover images are dithered down (now properly use the eInk palette of 16 shades of grey).
        * Reduced memory consumption of the cover processing, now less likely to blow up the framework on PW devices :).
        * In the same spirit, added more settings to control the dithering process (none/FloydSteinberg/Riemersma).
    
    * *v0.12.N*:
    
        * Disable autoreboot by default (if you're updating, consider disabling it yourself). Use the new KUAL button instead!
        * Updated binaries (updated tc)
    
    * *v0.13.N*:
    
        * Tweak the cover extraction process to try harder to pull something out of some mobi/prc files (without the CoverOffset EXTH metadata)
        * Slightly prettier verbose mode
        * Updated binaries (updated tc)
    
    * *v0.14.N*:
    
        * Fix a tiny part of the cover extraction fixes from v0.13.N… -_-"
        * Add a KUAL button to preview the current active cover in cover mode (in the Tools submenu)
    
    * *v0.15.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.16.N*:
    
        * PW2 support.
        * Updated binaries (updated tc, im)
    
    * *v0.17.N*:
    
        * Updated binaries (updated tc, im)
        * Optionally handle periodicals in cover mode
        * Better pinfo handling (thanks to dsmid)
    
    * *v0.18.N*:
    
        * Updated binaries (updated tc, im)
        * Handle the full range of 'new' PW2 models
    
    * *v0.19.N*:
    
        * Fix a very stupid bug present since the very first version, which led to the Hack generating covers in a slightly off resolution on the PW/PW2...
    
    * *v0.20.N*:
    
        * Fix a minor regression introduced in v0.19.N: if you _updated_ to 0.19.N, remove the *linkss/screensavers/00_you_can_delete_me-kv.png* file and update the hack!
    
    * *v0.21.N*:
    
        * Handle FW 5.6.x properly.
    
    * *v0.22.N*:
    
        * Updated binaries.
        * Fix the personal info watermark in cover mode on FW 5.6.1.x
        * Fix the "Restart framework now" KUAL button, so that it's now actually enough to reload the hack's settings. (f.g., switch to/from cover mode).
    
    * *v0.23.N*:
    
        * Updated binaries (updated tc, im).
        * Fix eips handling on the KT2.
    
    * *v0.24.N*:
    
        * Updated binaries (updated tc, im).
        * Minor tweaks to avoid cover mode misdetections on FW 5.6.x on the PW1 (... because it's slow as hell).
    
    * *v0.25.N*:
    
        * Updated binaries (updated tc, im).
        * KFX support in cover mode.
    

**Python*:

    * *v0.1.N*:
    
        * First release :).
    
    * *v0.2.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.3.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.4.N*:
    
        * Updated binaries (updated tc, update to Python 2.7.5)
    
    * *v0.5.N*:
    
        * Updated binaries (updated tc, updated Python 2.7.5 patchset to fix potential issues with the re module)
    
    * *v0.6.N*:
    
        * Updated binaries (updated tc, fixed ssl & pyexpat modules)
    
    * *v0.7.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.8.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.9.N*:
    
        * PW2 support.
        * Updated binaries (updated tc, update to Python 2.7.6)
    
    * *v0.10.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.11.N*:
    
        * Updated binaries (updated tc, update to Python 2.7.8, ships with a few third-party modules)
    
    * *v0.12.N*:
    
        * Updated binaries (update to Python 2.7.9)
        * The installer should no longer randomly fail in some circumstances (resource exhaustion).
    
    * *v0.13.N*:
    
        * Updated binaries (updated tc)
    
    * *v0.14.N*:
    
        * Updated binaries (updated tc, update to Python 2.7.10)
    
    * *v0.15.N*:
    
        * Updated binaries (updated tc, update to Python 2.7.15)
    

**Doc:* $Id: SS_MR_THREAD 16004 2019-06-04 17:09:41Z NiLuJe $


