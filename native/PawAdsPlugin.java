package com.luckydhananjaya.pawnote;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "PawAds")
public class PawAdsPlugin extends Plugin {

    @PluginMethod
    public void getAdConfig(PluginCall call) {
        JSObject res = new JSObject();
        boolean isDebug = BuildConfig.DEBUG;
        res.put("isDebug", isDebug);
        res.put("bannerAdUnitId", BuildConfig.BANNER_AD_ID);
        res.put("interstitialAdUnitId", BuildConfig.INTERSTITIAL_AD_ID);
        res.put("isTesting", BuildConfig.IS_TESTING);
        call.resolve(res);
    }
}
