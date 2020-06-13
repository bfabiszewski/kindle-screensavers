#!/bin/sh
#
# ScreenSavers installer
#
# $Id: install.sh 16252 2019-07-23 21:44:39Z NiLuJe $
#
##

HACKNAME="linkss"

# Pull libOTAUtils for logging & progress handling
[ -f ./libotautils5 ] && source ./libotautils5


otautils_update_progressbar

# Install our hack's custom content
# Check which default screensaver to use...
kmodel="$(cut -c3-4 /proc/usid)"
case "${kmodel}" in
    "13" | "54" | "2A" | "4F" | "52" | "53" )
        # Voyage...
        logmsg "I" "install" "" "using the default voyage custom screensaver"
        HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me.png ${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
    ;;
    "24" | "1B" | "1D" | "1F" | "1C" | "20" | "D4" | "5A" | "D5" | "D6" | "D7" | "D8" | "F2" | "17" | "60" | "F4" | "F9" | "62" | "61" | "5F" )
        # PaperWhite...
        logmsg "I" "install" "" "using the default paperwhite custom screensaver"
        HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me.png ${HACKNAME}/screensavers/00_you_can_delete_me-kv.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
    ;;
    "0F" | "11" | "10" | "12" | "C6" | "DD" )
        # Touch & KT2
        logmsg "I" "install" "" "using the default touch custom screensaver"
        HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-kv.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
    ;;
    * )
        # Try the new device ID scheme...
        kmodel="$(cut -c4-6 /proc/usid)"
        case "${kmodel}" in
            "0G1" | "0G2" | "0G4" | "0G5" | "0G6" | "0G7" | "0KB" | "0KC" | "0KD" | "0KE" | "0KF" | "0KG" | "0LK" | "0LL" | "0GC" | "0GD" | "0GR" | "0GS" | "0GT" | "0GU" | "0PP" | "0T1" | "0T2" | "0T3" | "0T4" | "0T5" | "0T6" | "0T7" | "0TJ" | "0TK" | "0TL" | "0TM" | "0TN" | "102" | "103" | "16Q" | "16R" | "16S" | "16T" | "16U" | "16V" )
                # PW3/PW4 & Oasis...
                logmsg "I" "install" "" "using the default paperwhite 3/4 & oasis custom screensaver"
                HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me.png ${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
            ;;
            "0DU" | "0K9" | "0KA" | "10L" | "0WF" | "0WG" | "0WH" | "0WJ" | "0VB" )
                # KT3/KT4...
                logmsg "I" "install" "" "using the default touch custom screensaver"
                HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-kv.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
            ;;
            "0LM" | "0LN" | "0LP" | "0LQ" | "0P1" | "0P2" | "0P6" | "0P7" | "0P8" | "0S1" | "0S2" | "0S3" | "0S4" | "0S7" | "0SA" | "11L" | "0WQ" | "0WP" | "0WN" | "0WM" | "0WL" )
                # Oasis 2/Oasis 3...
                logmsg "I" "install" "" "using the default oasis 2/3 custom screensaver"
                HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me.png ${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-kv.png"
            ;;
            * )
                # Fallback
                logmsg "I" "install" "" "using the default touch custom screensaver"
                HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-kv.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
            ;;
        esac
    ;;
esac

otautils_update_progressbar

# But keep the user's custom content...
if [ -d /mnt/us/${HACKNAME} ] ; then
    logmsg "I" "install" "" "our custom directory already exists, checking if we have custom content to preserve"
    # Custom Screensavers
    if [ "x$( ls -A /mnt/us/${HACKNAME}/screensavers 2> /dev/null )" != x ] ; then
        # If we already have a non-empty custom ss dir, exclude the default custom ss from our archive
        HACK_EXCLUDE="${HACKNAME}/screensavers/00_you_can_delete_me.png ${HACKNAME}/screensavers/00_you_can_delete_me-pw.png ${HACKNAME}/screensavers/00_you_can_delete_me-kv.png ${HACKNAME}/screensavers/00_you_can_delete_me-koa2.png"
        logmsg "I" "install" "" "found custom screensavers, excluding default custom screensaver"
    fi
    # If we disabled autoreboot, don't re-enable it...
    if [ ! -f /mnt/us/${HACKNAME}/autoreboot ] ; then
        HACK_EXCLUDE="${HACK_EXCLUDE} ${HACKNAME}/autoreboot"
        logmsg "I" "install" "" "keep autoreboot status (off)"
    fi
fi

otautils_update_progressbar

# Okay, now we can extract it. Since busybox's tar is very limited, we have to use a tmp directory to perform our filtering
logmsg "I" "install" "" "installing custom directory"
# Make sure our xzdec binary is executable first...
chmod +x ./xzdec
./xzdec ${HACKNAME}.tar.xz | tar -xvf -
# Do check if that went well
_RET=$?
if [ ${_RET} -ne 0 ] ; then
    logmsg "C" "install" "code=${_RET}" "failed to extract custom directory in tmp location"
    return 1
fi

otautils_update_progressbar

cd src
# And now we filter the content to preserve user's custom content
for custom_file in ${HACK_EXCLUDE} ; do
    if [ -f "./${custom_file}" ] ; then
        logmsg "I" "install" "" "preserving custom content (${custom_file})"
        rm -f "./${custom_file}"
    fi
done
# Finally, unleash our filtered dir on the live userstore
cp -af . /mnt/us/
_RET=$?
if [ ${_RET} -ne 0 ] ; then
    logmsg "C" "install" "code=${_RET}" "failure to update userstore with custom directory"
    return 1
fi
cd - >/dev/null
rm -rf src

otautils_update_progressbar

# Remove our deprecated content
# From simple_screensaver
logmsg "I" "install" "" "removing deprecated files (simple_screensaver)"
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

# From v0.6.N
logmsg "I" "install" "" "removing deprecated files (mobi_unpack)"
if [ -f /mnt/us/${HACKNAME}/bin/mobi_unpack.py ] ; then
    rm -f /mnt/us/${HACKNAME}/bin/mobi_unpack.py
fi
if [ -f /mnt/us/${HACKNAME}/bin/mobi_unpack.pyc ] ; then
    rm -f /mnt/us/${HACKNAME}/bin/mobi_unpack.pyc
fi
if [ -f /mnt/us/${HACKNAME}/bin/mobi_unpack.pyo ] ; then
    rm -f /mnt/us/${HACKNAME}/bin/mobi_unpack.pyo
fi

otautils_update_progressbar

# From v0.8.N
logmsg "I" "install" "" "removing deprecated files (old imagemagick config)"
if [ -d /mnt/us/${HACKNAME}/etc/ImageMagick ] ; then
    rm -rf /mnt/us/${HACKNAME}/etc/ImageMagick
fi

otautils_update_progressbar


# Setup startup script
logmsg "I" "install" "" "installing upstart job"
cp -f ${HACKNAME}.conf /etc/upstart/${HACKNAME}.conf

otautils_update_progressbar

# Generating Python bytecode for Mobi Unpack
logmsg "I" "install" "" "generating python bytecode"
# We need python, of course ;)
if [ -f "/mnt/us/python/bin/python2.7" ] ; then
    /mnt/us/python/bin/python2.7 -m py_compile /mnt/us/${HACKNAME}/bin/kindleunpack.py /mnt/us/${HACKNAME}/bin/mobi_uncompress.py /mnt/us/${HACKNAME}/bin/path.py /mnt/us/${HACKNAME}/bin/utf8_utils.py /mnt/us/${HACKNAME}/bin/kfxmeta.py
    /mnt/us/python/bin/python2.7 -O -m py_compile /mnt/us/${HACKNAME}/bin/kindleunpack.py /mnt/us/${HACKNAME}/bin/mobi_uncompress.py /mnt/us/${HACKNAME}/bin/path.py /mnt/us/${HACKNAME}/bin/utf8_utils.py /mnt/us/${HACKNAME}/bin/kfxmeta.py
fi

otautils_update_progressbar

logmsg "I" "install" "" "cleaning up"
rm -f ${HACKNAME}.conf ${HACKNAME}.tar.xz xzdec

logmsg "I" "install" "" "done"

otautils_update_progressbar

return 0
