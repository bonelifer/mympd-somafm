-- {"name":"SomaFM","file":"","version":0,"order":4,"arguments":[]}
local service = "http://127.0.0.1:18768"
local station = mympd_arguments.station
if mympd_env.scriptevent == "http" then
    local headers = "Content-Type: application/json\r\n"
    if type(station) ~= "string" or #station > 64 or not station:match("^[%w%-]+$") then
        return mympd.http_reply(400, headers, "[]")
    end
    local rc, status, _, body = mympd.http_client(
        "GET", service .. "/recent/" .. station, "", "", false
    )
    if rc ~= 0 or status ~= 200 then
        return mympd.http_reply(502, headers, "[]")
    end
    return mympd.http_reply(200, headers, body)
end
if station then
    if type(station) ~= "string" or not station:match("^[%w%-]+$") then
        return "Invalid SomaFM station"
    end
    local rc, status, _, body = mympd.http_client(
        "GET", service .. "/stations/" .. station, "", "", false
    )
    if rc ~= 0 or status ~= 200 then
        return "Could not resolve the SomaFM stream"
    end
    rc = mympd.api("MYMPD_API_QUEUE_APPEND_URIS", {
        uris = {json.decode(body).url}, play = true
    })
    return rc == 0 and "Started SomaFM station" or "Could not start SomaFM station"
end

local rc, status, _, body = mympd.http_client("GET", service .. "/stations", "", "", false)
if rc ~= 0 or status ~= 200 then
    return "Could not load SomaFM channels"
end
local urls, names = {}, {}
for _, item in ipairs(json.decode(body)) do
    urls[#urls + 1] = item.id
    names[#names + 1] = item.name
end
if #urls == 0 then
    return "No SomaFM channels found"
end
return mympd.dialog("SomaFM", {{
    name = "station", type = "select", value = urls,
    displayValue = names, defaultValue = urls[1]
}}, "SomaFM")
