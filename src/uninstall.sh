#!/bin/sh
#
# ScreenSavers uninstaller
#
# $Id: uninstall.sh 11231 2014-12-07 14:22:33Z NiLuJe $
#
##

HACKNAME="linkss"

# Pull libOTAUtils for logging & progress handling
[ -f ./libotautils5 ] && source ./libotautils5


otautils_update_progressbar

# Remove our deprecated content
# From simple_screensaver
logmsg "I" "uninstall" "" "removing deprecated files (simple_screensaver)"
# v1
if [ -f /etc/upstart/screensaver_hack.conf ] ; then
    rm -f /etc/upstart/screensaver_hack.conf
fi
# v2
if [ -f /etc/upstart/custom_screensaver.conf ] ; then
	rm -f /etc/upstart/custom_screensaver.conf
fi
if [ -f /usr/lib/blanket/custom_screensaver.so ] ; then
	# Bundle this here, since I have no idea how resilient blanket is,
	# and how well it would deal with trying to unload a non-existent module.
	lipc-set-prop com.lab126.blanket unload custom_screensaver
	rm -f /usr/lib/blanket/custom_screensaver.so
fi

otautils_update_progressbar

# Delete upstart job
logmsg "I" "uninstall" "" "removing upstart job"
if [ -f /etc/upstart/${HACKNAME}.conf ] ; then
    rm -f /etc/upstart/${HACKNAME}.conf
fi

otautils_update_progressbar

# Remove custom directory in userstore?
logmsg "I" "uninstall" "" "removing kual extension (only if /mnt/us/${HACKNAME}/uninstall exists)"
if [ -d /mnt/us/extensions/${HACKNAME} -a -f /mnt/us/${HACKNAME}/uninstall ] ; then
    rm -rf /mnt/us/extensions/${HACKNAME}
    logmsg "I" "uninstall" "" "kual extension has been removed"
fi
logmsg "I" "uninstall" "" "removing custom directory (only if /mnt/us/${HACKNAME}/uninstall exists)"
if [ -d /mnt/us/${HACKNAME} -a -f /mnt/us/${HACKNAME}/uninstall ] ; then
    rm -rf /mnt/us/${HACKNAME}
    logmsg "I" "uninstall" "" "custom directory has been removed"
fi

otautils_update_progressbar

logmsg "I" "uninstall" "" "done"

otautils_update_progressbar

return 0
