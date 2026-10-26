// SPDX-FileCopyrightText: Copyright 2026 bbport contributors
// SPDX-License-Identifier: GPL-2.0-or-later

// BBSC relay fallback - see p2p_relay.h. Ported from BBSC 0.0.2 (CLS_AMG, GPL-2.0-or-later).

#include "core/net/host_net.h" // the platform's socket headers first (winsock2 before windows.h)
#include "core/net/p2p_relay.h"

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <unordered_map>
#include <vector>

#include "common/logging/log.h"

namespace Core::Net::P2P::Relay {
namespace {

using Clock = std::chrono::steady_clock;

constexpr size_t kIdSize = 16;
constexpr size_t kEpSize = 6;
constexpr u8 kMagic[4] = {'B', 'B', 'R', '1'};
constexpr size_t kEarlyFrames = 32;

struct Peer {
    std::string id;
    u32 addr{};
    u16 port{};
    bool relayed{false};
    bool direct_rx{false};
    bool tx_started{false};
    bool relay_seen{false}; // it sent to us through the relay (it has the relay too)
    Clock::time_point first_tx{};
    Clock::time_point relayed_since{};
    // The relay said it is not registered (no relay in its emulator, or not running): direct
    // only until then (asked again after it).
    Clock::time_point missing_until{};
    bool missing_logged{false};
    std::vector<std::vector<u8>> early; // sent directly before the switch (sent again then)
};

struct State {
    std::mutex mutex;
    u32 server_addr{0};
    u16 server_port{0};
    bool force{true};
    bool acked{false};
    u32 self_addr{0};
    u16 self_port{0};
    Clock::time_point last_register{};
    std::vector<std::string> local_ids;
    std::unordered_map<std::string, Peer> peers;     // by padded online id
    std::unordered_map<u64, std::string> alias;      // every known endpoint -> online id
    u32 next_pseudo{1};
    u64 sent{0};
    u64 received{0};
    Clock::time_point last_status{};
    u64 status_sent{0};
    u64 status_received{0};
};

State& S() {
    static State state;
    return state;
}

const char* Env(const char* primary, const char* fallback) {
    const char* value = std::getenv(primary);
    if (value == nullptr || *value == 0) {
        value = std::getenv(fallback);
    }
    return value != nullptr ? value : "";
}

std::string PadId(std::string_view online_id) {
    std::string id(online_id.substr(0, std::min(online_id.size(), kIdSize)));
    id.resize(kIdSize, static_cast<char>(0));
    return id;
}

std::string IdText(const std::string& id) {
    return std::string(id.c_str());
}

u64 EndpointKey(u32 addr_nbo, u16 port_nbo) {
    return (static_cast<u64>(addr_nbo) << 16) | port_nbo;
}

// mutex held.
void AddAliasLocked(State& s, const std::string& id, u32 addr_nbo, u16 port_nbo,
                    const char* from) {
    if (addr_nbo == 0 || port_nbo == 0) {
        return;
    }
    const u64 key = EndpointKey(addr_nbo, port_nbo);
    const auto it = s.alias.find(key);
    if (it != s.alias.end() && it->second == id) {
        return;
    }
    s.alias[key] = id;
    LOG_WARNING(Lib_Net, "P2P relay: '{}' known at {:#x}:{} (from {})", IdText(id), addr_nbo,
             ntohs(port_nbo), from);
}

// mutex held.
Peer* FindPeerLocked(State& s, u32 addr_nbo, u16 port_nbo) {
    const auto alias = s.alias.find(EndpointKey(addr_nbo, port_nbo));
    if (alias == s.alias.end()) {
        return nullptr;
    }
    const auto it = s.peers.find(alias->second);
    return it == s.peers.end() ? nullptr : &it->second;
}

// mutex held.
void SendRelayedLocked(State& s, const Peer& peer, std::span<const u8> framed,
                       const RawSend& send) {
    const std::string& self = s.local_ids.front();
    std::vector<u8> packet;
    packet.reserve(5 + 2 * kIdSize + kEpSize + framed.size());
    packet.insert(packet.end(), std::begin(kMagic), std::end(kMagic));
    packet.push_back(0x03);
    packet.insert(packet.end(), peer.id.begin(), peer.id.end());
    packet.insert(packet.end(), self.begin(), self.end());
    u8 ep[kEpSize];
    std::memcpy(ep, &s.self_addr, 4);
    std::memcpy(ep + 4, &s.self_port, 2);
    packet.insert(packet.end(), ep, ep + kEpSize);
    packet.insert(packet.end(), framed.begin(), framed.end());
    send(packet, s.server_addr, s.server_port);
    ++s.sent;
}

} // namespace

void SetServer(u32 addr_nbo) {
    State& s = S();
    std::lock_guard lock(s.mutex);
    const std::string mode = Env("BB_P2P_RELAY", "SHADPS4_P2P_RELAY");
    s.force = mode != "auto" && mode != "direct";
    u16 port = 3478;
    if (const std::string p = Env("BB_P2P_RELAY_PORT", "SHADPS4_P2P_RELAY_PORT"); !p.empty()) {
        const long parsed = std::strtol(p.c_str(), nullptr, 10);
        if (parsed > 0 && parsed < 65536) {
            port = static_cast<u16>(parsed);
        }
    }
    if (mode == "0" || mode == "off") {
        addr_nbo = 0;
    } else if (const size_t colon = mode.find(':'); colon != std::string::npos) {
        // "a.b.c.d:port": a relay other than the shadNet server's (tests).
        in_addr parsed{};
        const long parsed_port = std::strtol(mode.c_str() + colon + 1, nullptr, 10);
        if (addr_nbo != 0 && inet_pton(AF_INET, mode.substr(0, colon).c_str(), &parsed) == 1 &&
            parsed_port > 0 && parsed_port < 65536) {
            std::memcpy(&addr_nbo, &parsed, 4);
            port = static_cast<u16>(parsed_port);
        }
    }
    const u16 port_nbo = addr_nbo != 0 ? htons(port) : 0;
    if (s.server_addr == addr_nbo && s.server_port == port_nbo) {
        return;
    }
    s.server_addr = addr_nbo;
    s.server_port = port_nbo;
    s.acked = false;
    s.last_register = {};
    if (addr_nbo != 0) {
        LOG_WARNING(Lib_Net, "P2P relay: server {:#x}:{}{}", addr_nbo, port,
                 s.force ? " (every peer through it, direct copies until a peer answers)"
                         : " (direct first, relay after 2 s)");
    } else {
        LOG_WARNING(Lib_Net, "P2P relay: off");
    }
}

void SetSelfEndpoint(u32 addr_nbo, u16 port_nbo) {
    State& s = S();
    std::lock_guard lock(s.mutex);
    if (s.self_addr != addr_nbo || s.self_port != port_nbo) {
        LOG_WARNING(Lib_Net, "P2P relay: our public endpoint {:#x}:{}", addr_nbo, ntohs(port_nbo));
    }
    s.self_addr = addr_nbo;
    s.self_port = port_nbo;
}

void SetLocalId(std::string_view online_id) {
    if (online_id.empty()) {
        return;
    }
    State& s = S();
    std::lock_guard lock(s.mutex);
    const std::string id = PadId(online_id);
    if (std::find(s.local_ids.begin(), s.local_ids.end(), id) == s.local_ids.end()) {
        s.local_ids.push_back(id);
        s.last_register = {};
        LOG_WARNING(Lib_Net, "P2P relay: our id '{}'", IdText(id));
    }
}

void RememberPeer(std::string_view online_id, u32 addr_nbo, u16 port_nbo) {
    if (online_id.empty() || addr_nbo == 0 || port_nbo == 0) {
        return;
    }
    State& s = S();
    std::lock_guard lock(s.mutex);
    const std::string id = PadId(online_id);
    // Peers are kept by online id; every endpoint signaling or the relay ever gave for it stays
    // an alias (a peer filed under one endpoint only got one-way relay behind CGNAT).
    Peer& peer = s.peers[id];
    peer.id = id;
    peer.addr = addr_nbo; // the endpoint signaling uses: relayed frames arrive "from" it
    peer.port = port_nbo;
    AddAliasLocked(s, id, addr_nbo, port_nbo, "signaling");
}

bool Enabled() {
    State& s = S();
    std::lock_guard lock(s.mutex);
    return s.server_addr != 0 && !s.local_ids.empty();
}

bool IsServer(u32 addr_nbo, u16 port_nbo) {
    State& s = S();
    std::lock_guard lock(s.mutex);
    return s.server_addr != 0 && addr_nbo == s.server_addr && port_nbo == s.server_port;
}

Path Route(u32 dest_addr_nbo, u16 dest_port_nbo, std::span<const u8> packet,
           const RawSend& send) {
    State& s = S();
    std::lock_guard lock(s.mutex);
    if (s.server_addr == 0 || s.local_ids.empty() || dest_addr_nbo == s.server_addr) {
        return Path::Direct;
    }
    Peer* const found = FindPeerLocked(s, dest_addr_nbo, dest_port_nbo);
    if (found == nullptr) {
        return Path::Direct;
    }
    Peer& peer = *found;
    const auto now = Clock::now();
    if (peer.relayed && now < peer.missing_until) {
        return Path::Direct;
    }
    if (!peer.relayed) {
        if (s.force) {
            peer.relayed = true;
        } else if (!peer.tx_started) {
            peer.tx_started = true;
            peer.first_tx = now;
        } else if (!peer.direct_rx && now - peer.first_tx >= std::chrono::seconds(2)) {
            peer.relayed = true;
        }
        if (!peer.relayed) {
            // Kept for the switch: signaling sends some packets only once; lost directly, the
            // peer ignores everything after them and the connection dies after 30 s.
            if (!peer.direct_rx && peer.early.size() < kEarlyFrames) {
                peer.early.emplace_back(packet.begin(), packet.end());
            }
            return Path::Direct;
        }
        peer.relayed_since = now;
        LOG_WARNING(Lib_Net, "P2P relay: '{}' at {:#x}:{} {} - through the relay ({} earlier "
                          "frame(s) sent again)",
                 IdText(peer.id), peer.addr, ntohs(peer.port),
                 s.force ? "(every peer)" : "sent nothing back directly in 2 s",
                 peer.early.size());
        for (const std::vector<u8>& early : peer.early) {
            SendRelayedLocked(s, peer, early, send);
        }
        peer.early.clear();
        peer.early.shrink_to_fit();
    }
    SendRelayedLocked(s, peer, packet, send);
    const bool direct_copy =
        !peer.direct_rx &&
        (!peer.relay_seen || now - peer.relayed_since < std::chrono::seconds(10));
    return direct_copy ? Path::Both : Path::Relay;
}

void NoteDirectReceive(u32 addr_nbo, u16 port_nbo) {
    State& s = S();
    std::lock_guard lock(s.mutex);
    if (s.peers.empty()) {
        return;
    }
    Peer* const found = FindPeerLocked(s, addr_nbo, port_nbo);
    if (found == nullptr || found->direct_rx) {
        return;
    }
    Peer& peer = *found;
    peer.direct_rx = true;
    peer.early.clear();
    if (peer.relayed && !peer.relay_seen) {
        // It answers directly and never used the relay (an emulator without it, or a NAT hole
        // that took longer to open): direct from now on.
        peer.relayed = false;
        LOG_WARNING(Lib_Net, "P2P relay: '{}' reached us directly - back to direct", IdText(peer.id));
    } else {
        LOG_WARNING(Lib_Net, "P2P relay: '{}' reached us directly{}", IdText(peer.id),
                 peer.relayed ? " (staying on the relay)" : "");
    }
}

bool Receive(std::span<const u8> data, std::span<const u8>* frame, u32* from_addr_nbo,
             u16* from_port_nbo) {
    if (data.size() < 5 || std::memcmp(data.data(), kMagic, 4) != 0) {
        return false;
    }
    State& s = S();
    const u8 kind = data[4];
    if (kind == 0x02) {
        std::lock_guard lock(s.mutex);
        if (!s.acked) {
            s.acked = true;
            LOG_WARNING(Lib_Net, "P2P relay: registered with the relay");
        }
        return false;
    }
    if (kind == 0x05 && data.size() >= 5 + kIdSize) {
        const std::string id(reinterpret_cast<const char*>(data.data() + 5), kIdSize);
        std::lock_guard lock(s.mutex);
        const auto known = s.peers.find(id);
        if (known != s.peers.end()) {
            Peer& peer = known->second;
            peer.missing_until = Clock::now() + std::chrono::seconds(10);
            if (!peer.missing_logged) {
                peer.missing_logged = true;
                LOG_WARNING(Lib_Net,
                            "P2P relay: '{}' is not on the relay (its emulator has no BBSC relay, "
                            "or it is not running) - direct only",
                            IdText(peer.id));
            }
        }
        return false;
    }
    if (kind != 0x04 || data.size() < 5 + kIdSize + kEpSize) {
        return false;
    }
    const std::string id(reinterpret_cast<const char*>(data.data() + 5), kIdSize);
    u32 ep_addr = 0;
    u16 ep_port = 0;
    std::memcpy(&ep_addr, data.data() + 5 + kIdSize, 4);
    std::memcpy(&ep_port, data.data() + 5 + kIdSize + 4, 2);
    {
        std::lock_guard lock(s.mutex);
        if (!s.peers.contains(id)) {
            // A peer signaling never looked up: the endpoint it gave, else a made-up one
            // (169.254.x.x, never sent to directly) so the answers go back through the relay.
            Peer& made = s.peers[id];
            made.id = id;
            if (ep_addr != 0 && ep_port != 0) {
                made.addr = ep_addr;
                made.port = ep_port;
            } else {
                made.addr = htonl(0xA9FE0000u | (s.next_pseudo++ & 0xFFFFu));
                made.port = htons(3173);
            }
            AddAliasLocked(s, id, made.addr, made.port, "relay, new peer");
        }
        // Its own endpoint is one more alias; the peer keeps the endpoint signaling knows, so
        // the frame arrives from where signaling expects it.
        AddAliasLocked(s, id, ep_addr, ep_port, "relay");
        Peer& peer = s.peers[id];
        peer.relay_seen = true;
        peer.missing_until = {};
        if (!peer.relayed) {
            peer.relayed = true;
            peer.relayed_since = Clock::now();
            LOG_WARNING(Lib_Net, "P2P relay: '{}' reached us through the relay - answering the same "
                              "way",
                     IdText(peer.id));
        }
        ++s.received;
        *from_addr_nbo = peer.addr;
        *from_port_nbo = peer.port;
    }
    const size_t head = 5 + kIdSize + kEpSize;
    *frame = data.subspan(head);
    return true;
}

void KeepAlive(const RawSend& send) {
    State& s = S();
    std::lock_guard lock(s.mutex);
    if (s.server_addr == 0 || s.local_ids.empty()) {
        return;
    }
    const auto now = Clock::now();
    const auto interval = s.acked ? std::chrono::seconds(5) : std::chrono::seconds(2);
    if (s.last_register.time_since_epoch().count() != 0 && now - s.last_register < interval) {
        return;
    }
    s.last_register = now;
    if (now - s.last_status >= std::chrono::seconds(30) &&
        (s.sent != s.status_sent || s.received != s.status_received)) {
        s.last_status = now;
        s.status_sent = s.sent;
        s.status_received = s.received;
        std::string peers;
        for (const auto& [id, peer] : s.peers) {
            if (!peers.empty()) {
                peers += ", ";
            }
            peers += IdText(peer.id);
            peers += !peer.relayed                ? " direct"
                     : now < peer.missing_until   ? " not on the relay"
                     : peer.relay_seen            ? " relay"
                                                  : " relay (no answer yet)";
        }
        LOG_WARNING(Lib_Net, "P2P relay: {} frame(s) sent / {} received through the relay so far; "
                          "peers: {}",
                 s.sent, s.received, peers.empty() ? "none" : peers);
    }
    for (const std::string& id : s.local_ids) {
        std::vector<u8> packet(std::begin(kMagic), std::end(kMagic));
        packet.push_back(0x01);
        packet.insert(packet.end(), id.begin(), id.end());
        send(packet, s.server_addr, s.server_port);
    }
}

} // namespace Core::Net::P2P::Relay
