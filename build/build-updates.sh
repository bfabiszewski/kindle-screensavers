#!/bin/bash -e
#
# $Id: build-updates.sh 16256 2019-07-23 22:04:59Z NiLuJe $
#

HACKNAME="linkss"
HACKDIR="ScreenSavers"
PKGNAME="${HACKNAME}"
PKGVER="0.25.N.mobitool"

# Setup KindleTool packaging metadata flags to avoid cluttering the invocations
# PKGREV="$(svnversion -c .. | awk '{print $NF}' FS=':' | tr -d 'P')"
PKGREV=0
KT_PM_FLAGS=( "-xPackageName=${HACKDIR}" "-xPackageVersion=${PKGVER}-r${PKGREV}" "-xPackageAuthor=NiLuJe" "-xPackageMaintainer=NiLuJe" )

# We need kindletool (https://github.com/NiLuJe/KindleTool) in $PATH
if (( $(kindletool version | wc -l) == 1 )) ; then
	HAS_KINDLETOOL="true"
fi

if [[ "${HAS_KINDLETOOL}" != "true" ]] ; then
	echo "You need KindleTool (https://github.com/NiLuJe/KindleTool) to build this package."
	exit 1
fi

# We also need GNU tar
if [[ "$(uname -s)" == "Darwin" ]] ; then
	TAR_BIN="gtar"
else
	TAR_BIN="tar"
fi
if ! ${TAR_BIN} --version | grep -q "GNU tar" ; then
	echo "You need GNU tar to build this package."
	exit 1
fi

## Install

# # Go away if we don't have the PW2 tree checked out for the A9 binaries...
# if [[ ! -d "../../../PW2_Hacks" ]] ; then
# 	echo "Skipping ScreenSavers build, we're missing the A9 binaries (from the PW2_Hacks tree)"
# 	exit 1
# fi

# ## Go away if we don't have the MobiCover tree checked out...
# if [[ ! -d "../../MobiCover" ]] ; then
# 	echo "Skipping ScreenSavers build, we're missing MobiCover"
# 	exit 1
# fi

# ## Go away if we don't have the ScreenSavers tree for the legacy version checked out...
# if [[ ! -d "../../../Hacks/ScreenSavers" ]] ; then
# 	echo "Skipping ScreenSavers build, we're missing the KUAL extension (from the Hacks tree)"
# 	exit 1
# fi

# # Pickup our common stuff... We leave it in our staging wd so it ends up in the source package.
# if [[ ! -d "../../Common" ]] ; then
# 	echo "The tree isn't checked out in full, missing the Common directory..."
# 	exit 1
# fi
# # LibOTAUtils 5
# ln -f ../../Common/lib/libotautils5 ./libotautils5
# # XZ Utils
ln -f kindle_binaries/KT/bin/xzdec ./xzdec
# # LibKH 5
# for common_lib in libkh5 ; do
# 	ln -f ../../Common/lib/${common_lib} ../src/${HACKNAME}/bin/${common_lib}
# done
# # USB Watchdog
# for common_bin in usb-watchdog usb-watchdog-helper ; do
# 	ln -f ../../Common/bin/${common_bin} ../src/${HACKNAME}/bin/${common_bin}
# done
# # FBInk
# ln -f ../../Common/bin/fbink ../src/${HACKNAME}/bin/fbink

# # Make sure we bundle our KUAL extension...
# cp -avf ../../../Hacks/ScreenSavers/src/extensions ../src/

# # mobitool (./configure --with-libxml2=no  --enable-tools-static && make)
# ln -f ../../libmobi/tools/mobitool ../src/${HACKNAME}/bin/mobitool


# Archive custom directory
export XZ_DEFAULTS="-T 0"
${TAR_BIN} --hard-dereference --owner root --group root --exclude-vcs -cvJf ${HACKNAME}.tar.xz ../src/${HACKNAME} ../src/extensions

# Copy the script to our working directory, to avoid storing crappy paths in the update package
ln -f ../src/install.sh ./
ln -f ../src/${HACKNAME}.conf ./

# Build the install package (Touch & PaperWhite)
kindletool create ota2 "${KT_PM_FLAGS[@]}" -d touch -d paperwhite libotautils5 install.sh ${HACKNAME}.tar.xz xzdec ${HACKNAME}.conf Update_${PKGNAME}_${PKGVER}_install_touch_pw.bin

# Remove the Touch & PaperWhite archive
rm -f ./${HACKNAME}.tar.xz

# Build the PaperWhite 2 archive...
${TAR_BIN} --hard-dereference --owner root --group root --exclude-vcs -cvf ${HACKNAME}.tar ../src/${HACKNAME} ../src/extensions
# Delete A8 binaries
KINDLE_MODEL_BINARIES="bin/convert bin/mogrify bin/identify bin/inotifywait bin/shlock bin/sort lib/libz.so.1 lib/libpng16.so.16 lib/libharfbuzz.so.0 lib/libfreetype.so.6 lib/libturbojpeg.so.0 lib/libjpeg.so.62 lib/libMagickWand-6.Q8.so.6 lib/libMagickCore-6.Q8.so.6"
for my_bin in ${KINDLE_MODEL_BINARIES} ; do
	${TAR_BIN} --delete -vf ${HACKNAME}.tar src/${HACKNAME}/${my_bin}
done
# Append A9 binaries
for my_bin in ${KINDLE_MODEL_BINARIES} ; do
	${TAR_BIN} --hard-dereference --owner root --group root --transform "s,^kindle_binaries/PW2/,src/${HACKNAME}/,S" --show-transformed-names -rvf ${HACKNAME}.tar kindle_binaries/PW2/${my_bin}
done
# Do the same for FBInk
${TAR_BIN} --delete -vf ${HACKNAME}.tar src/${HACKNAME}/bin/fbink
${TAR_BIN} --hard-dereference --owner root --group root --transform "s,^kindle_binaries/PW2/,src/${HACKNAME}/,S" --show-transformed-names -rvf ${HACKNAME}.tar kindle_binaries/PW2/bin/fbink
# xz it...
xz ${HACKNAME}.tar

# Speaking of, we need our own xzdec binary, too!
ln -f kindle_binaries/PW2/bin/xzdec ./xzdec

# Build the install package (>= Wario)
kindletool create ota2 "${KT_PM_FLAGS[@]}" -d paperwhite2 -d basic -d voyage -d paperwhite3 -d oasis -d basic2 -d oasis2 -d paperwhite4 -d basic3 -d oasis3 libotautils5 install.sh ${HACKNAME}.tar.xz xzdec ${HACKNAME}.conf Update_${PKGNAME}_${PKGVER}_install_pw2_kt2_kv_pw3_koa_kt3_koa2_pw4_kt4.bin

## Uninstall
# Copy the script to our working directory, to avoid storing crappy paths in the update package
ln -f ../src/uninstall.sh ./

# Build the uninstall package
kindletool create ota2 "${KT_PM_FLAGS[@]}" -d kindle5 libotautils5 uninstall.sh Update_${PKGNAME}_${PKGVER}_uninstall.bin

## Cleanup
# Remove package specific temp stuff
rm -f ./install.sh ./uninstall.sh ./${HACKNAME}.tar.xz ./xzdec ./${HACKNAME}.conf

# Move our updates
mv -f *.bin ../
