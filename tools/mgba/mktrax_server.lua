--
-- small server script for mgba that allows a network app to write data to the GBA's memory
-- listens on localhost:51337
--
-- api is:
--   POKE aaaaaaaa dddd         <-- write 16 bits; aaaaaaaa is a hex memory address to write to; dddd is 16 bits in hex to write
--


local print = function(...) console:log(...) end

local port = 51337
server = nil
conn = nil


function sock_error()
    print("ERR: socket error; dropping")
    if conn then
        conn:close()
        conn = nil
    end
end


function sock_receive()
    if not conn then
        print("ERR: sock_receive called without a sock?")
        return
    end

    -- process until the socket has no more cached data
    while true do
        local packet,err = conn:receive(1024)
        if err then
            if err ~= socket.ERRORS.AGAIN then
                sock_error()
            end
            return
        end

        print("MSG: received '" .. packet .. "'")
        local addr,val = packet:match("^POKE (%x%x%x%x%x%x%x%x) (%x%x%x%x)%s+")
        if addr then
            print("  .. poking: " .. addr .. " <-- " .. val)
            addr = tonumber(addr, 16)
            val = tonumber(val, 16)

            local oldval = emu:read16(addr)
            emu:write16(addr, val)
            print("  .. done! old val was " .. oldval)
        else
            print("WRN: invalid command: '" .. packet .. "'")
        end
    end
end


function sock_accept()
    print("SRV: accept!")

    local sock, err = server:accept()
    if err then
        print("ERR: failed to accept: " .. err)
        return
    end

    if conn then
        print("WRN: dropping connection as we have one already")
        sock:close()
        return
    end
    
    conn = sock
    conn:add("received", sock_receive)
    conn:add("error", sock_error)
end



function startup_server()
    local err, ok

    server, err = socket.bind(nil, port)
    if err then
        print("ERR: failed to bind to port " .. port .. ": " .. err)
        return
    end

    ok, err = server:listen()
    if err then
        server:close()
        print("ERR: failed to listen: " .. err)
        return
	end

    print("SRV: listening on port " .. port .. "...")
    server:add("received", sock_accept)
end

startup_server()


