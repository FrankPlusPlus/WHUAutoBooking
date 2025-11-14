function FindProxyForURL(url, host) {
    // 把需要抓的域名都放在这里
    if (shExpMatch(host, "dxvip.dingxiang-inc.com") ||
        shExpMatch(host, "static4.dingxiang-inc.com")) {
        return "PROXY 127.0.0.1:8080";
    }
    return "DIRECT";
}