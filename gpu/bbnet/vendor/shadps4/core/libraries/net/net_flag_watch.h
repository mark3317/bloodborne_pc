// SPDX-FileCopyrightText: Copyright 2026 bbport
// SPDX-License-Identifier: GPL-2.0-or-later
//
// bbport research 2026-10-27 (BBSC "each player's own NPC quests"): the game passes a talk's event
// flags to the other players by itself (the host's Eileen flags 9074 / 72410540 reached the guest
// without the game's SetFlag). To find that packet, every game P2P datagram / stream chunk the
// game sends or receives is scanned for the numbers of the NPC quest flags (BBSC's
// BbscNpcQuestFlags: every flag a talk script reads or sets), little- and big-endian at any
// offset; a hit is logged (Lib.Net) with the socket, vport, length and the first bytes - once per
// direction / vport / length / flag, at most 400 lines a run. Cheap: a range check per offset,
// a binary search only for values in the flags' range.
#pragma once

#include <algorithm>
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <mutex>
#include <set>
#include <string>
#include <tuple>
#include <fmt/format.h>
#include "common/logging/log.h"

namespace Libraries::Net::FlagWatch {

inline constexpr std::array<std::uint32_t, 788> NpcQuestFlags{
    706, 751, 760, 762, 764, 1102, 1103, 1104, 1105, 1106,
    1108, 1109, 1121, 1122, 1123, 1124, 1140, 1141, 1142, 1143,
    1144, 1145, 1146, 1147, 1148, 1149, 1160, 1161, 1163, 1164,
    1165, 1166, 1167, 1168, 1169, 1180, 1181, 1183, 1184, 1185,
    1186, 1187, 1188, 1189, 1190, 1193, 1194, 1200, 1202, 1204,
    1205, 1207, 1208, 1209, 1211, 1220, 1222, 1223, 1224, 1225,
    1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1240, 1241,
    1242, 1243, 1244, 1245, 1260, 1261, 1262, 1263, 1264, 1265,
    1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1280, 1281,
    1290, 1291, 1292, 1300, 1301, 1304, 1305, 1306, 1307, 1308,
    1309, 1311, 1313, 1314, 1320, 1321, 1322, 1323, 1324, 1325,
    1340, 1341, 1342, 1344, 1345, 1346, 1347, 1348, 1349, 1350,
    1351, 1360, 1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368,
    1369, 1370, 1371, 1372, 1381, 1382, 1400, 1401, 1402, 1420,
    1421, 1422, 1423, 1430, 1431, 1439, 1441, 1442, 1650, 1660,
    1670, 1671, 1672, 1710, 1711, 1712, 1713, 1720, 1721, 1722,
    1723, 1725, 1726, 1727, 1730, 1735, 1750, 1751, 1752, 1760,
    1761, 1762, 1770, 1780, 1790, 1800, 1801, 1805, 1930, 1933,
    1936, 1939, 1942, 1945, 1948, 1951, 1954, 1957, 1960, 1963,
    1966, 1969, 1975, 1978, 6000, 6300, 6302, 6303, 6305, 6308,
    6309, 6311, 6603, 6676, 6678, 6700, 6701, 6702, 6703, 6704,
    6705, 6706, 6707, 6708, 6709, 6710, 6711, 6712, 6713, 6714,
    6715, 6716, 6717, 6718, 6719, 6722, 6723, 6744, 6745, 6746,
    6747, 6749, 6750, 6751, 6753, 6754, 6755, 6756, 6757, 6758,
    6759, 6760, 6770, 6810, 6811, 6812, 6814, 9042, 9045, 9047,
    9048, 9049, 9050, 9051, 9052, 9053, 9054, 9055, 9056, 9057,
    9058, 9059, 9060, 9061, 9062, 9063, 9064, 9066, 9067, 9069,
    9071, 9072, 9073, 9074, 9075, 9077, 9430, 9431, 9432, 70000007,
    70000030, 70000050, 70000051, 70000052, 70000053, 70000054, 70000070, 70000071, 70000072, 70000073,
    70000074, 70000075, 70000100, 70000140, 70000230, 70000231, 70002401, 70002413, 72000000, 72200100,
    72200600, 72200601, 72300300, 72300301, 72300304, 72300305, 72300306, 72300307, 72300310, 72300313,
    72300314, 72300315, 72400105, 72400300, 72400301, 72400302, 72400303, 72400304, 72400305, 72400306,
    72400307, 72400309, 72400310, 72400311, 72400312, 72400313, 72400314, 72400315, 72400316, 72400317,
    72400318, 72400319, 72400320, 72400321, 72400322, 72400323, 72400324, 72400330, 72400331, 72400332,
    72400340, 72400341, 72400342, 72400343, 72400344, 72400345, 72400346, 72400347, 72400348, 72400349,
    72400350, 72400353, 72400354, 72400356, 72400360, 72400361, 72400362, 72400363, 72400370, 72400372,
    72400373, 72400374, 72400380, 72400381, 72400383, 72400384, 72400385, 72400390, 72400392, 72400393,
    72400394, 72400397, 72400398, 72400440, 72400441, 72400460, 72400461, 72400462, 72400463, 72400465,
    72400466, 72400467, 72400469, 72400470, 72400471, 72400474, 72400480, 72400484, 72400485, 72400486,
    72400489, 72400490, 72400491, 72400497, 72400498, 72400499, 72400500, 72400501, 72400502, 72400503,
    72400510, 72400511, 72400512, 72400513, 72400520, 72400521, 72400522, 72400523, 72400524, 72400525,
    72400526, 72400527, 72400528, 72400530, 72400900, 72400914, 72400915, 72400916, 72400920, 72400921,
    72400924, 72400933, 72400934, 72400935, 72400936, 72400937, 72400938, 72400950, 72400953, 72400954,
    72400955, 72400960, 72400961, 72400962, 72400963, 72400964, 72400965, 72400966, 72400970, 72400971,
    72400972, 72400980, 72400981, 72400982, 72409900, 72409901, 72409910, 72409920, 72409930, 72410300,
    72410301, 72410302, 72410303, 72410304, 72410305, 72410306, 72410307, 72410308, 72410309, 72410310,
    72410311, 72410320, 72410321, 72410322, 72410323, 72410325, 72410326, 72410327, 72410328, 72410329,
    72410330, 72410331, 72410332, 72410333, 72410334, 72410335, 72410336, 72410337, 72410338, 72410339,
    72410340, 72410341, 72410342, 72410343, 72410344, 72410345, 72410346, 72410347, 72410348, 72410349,
    72410350, 72410351, 72410352, 72410353, 72410354, 72410355, 72410356, 72410357, 72410358, 72410359,
    72410360, 72410361, 72410362, 72410363, 72410364, 72410365, 72410366, 72410370, 72410371, 72410380,
    72410382, 72410383, 72410384, 72410385, 72410390, 72410391, 72410392, 72410393, 72410394, 72410400,
    72410401, 72410402, 72410403, 72410404, 72410405, 72410406, 72410407, 72410412, 72410413, 72410414,
    72410415, 72410416, 72410420, 72410421, 72410422, 72410423, 72410461, 72410462, 72410500, 72410501,
    72410502, 72410503, 72410504, 72410505, 72410506, 72410511, 72410512, 72410513, 72410514, 72410515,
    72410516, 72410520, 72410521, 72410530, 72410540, 72410541, 72410542, 72410543, 72410544, 72410545,
    72410546, 72410600, 72410601, 72410602, 72410603, 72410610, 72410611, 72410612, 72410614, 72410615,
    72410630, 72410631, 72410632, 72410633, 72410634, 72500301, 72500302, 72500304, 72500310, 72500311,
    72500312, 72500320, 72500321, 72500322, 72500326, 72500329, 72500330, 72500331, 72500332, 72500333,
    72500334, 72500335, 72500336, 72500337, 72500339, 72500340, 72500341, 72500342, 72500343, 72500344,
    72500345, 72500346, 72500347, 72500348, 72500356, 72500357, 72500600, 72500601, 72500602, 72500604,
    72600300, 72600301, 72600302, 72600303, 72600304, 72600305, 72600306, 72600311, 72600316, 72600317,
    72700300, 72700301, 72700302, 72700303, 72700304, 72700305, 72700306, 72700321, 72700322, 72700330,
    72700360, 72700361, 72700364, 72700374, 72700440, 72700443, 72700444, 72700445, 72700450, 72700451,
    72800301, 72800302, 72800304, 72800305, 72800306, 72800307, 72800308, 72800309, 72800310, 72800311,
    72800312, 72800313, 72800314, 72800315, 72800316, 72900000, 72900001, 72900002, 72910000, 72910020,
    72910030, 73200300, 73200320, 73200321, 73200322, 73200323, 73200324, 73200325, 73200326, 73200327,
    73200330, 73200331, 73200332, 73200333, 73200334, 73200335, 73200340, 73200341, 73200342, 73200343,
    73200344, 73200350, 73200351, 73200352, 73200353, 73200354, 73200355, 73400400, 73400401, 73400402,
    73400403, 73400404, 73400405, 73400422, 73400423, 73400424, 73400430, 73400431, 73400510, 73400511,
    73400512, 73400513, 73500300, 73500301, 73500302, 73500303, 73500305, 73500306, 73500308, 73500309,
    73500310, 73500311, 73500312, 73500315, 73500316, 73500317, 73500318, 73500319, 73500320, 73500321,
    73500322, 73500326, 73500327, 73500338, 73500339, 73500400, 73500401, 73500402, 73500410, 73500411,
    73500412, 73500414, 73500415, 73500500, 73500501, 73500502, 73500505, 73500600, 73500601, 73500602,
    73500621, 73500630, 73500900, 73500905, 73500910, 73500911, 73500915, 73500920, 73500925, 73500930,
    73500935, 73500936, 73500945, 73500946, 73500950, 73500955, 73500960, 73500965, 73500970, 73500971,
    73500974, 73500975, 73500976, 73500979, 73500980, 73500981, 73600300, 73600301, 73600310, 73600311,
    73600312, 73600313, 73600314, 73600315, 73600318, 73600500, 73600501, 73600503, 73600520, 73600521,
    73600530, 79900100, 79900104, 79900106, 79900107, 79900108, 79900109, 79900111
};

// 2026-10-27, second pass: the first run found no flag number in any game packet - the game may
// pass the talk-driven events themselves (EMEVD 2000[02] "network sync" / 1000[09] "event result
// network approval"), so the ids of the 129 talk-driven events (BBSC BbscTalkEventTriggers) and the
// flag group keys of their triggers (flag / 1000) are looked for too.
inline constexpr std::array<std::uint32_t, 129> TalkEvents{7200, 9040, 9100, 9700, 9701, 9702, 9703, 9710, 9720, 9780, 12100110, 12100112, 12100113, 12100116, 12100123, 12100161, 12100165, 12100180, 12101022, 12101024, 12101026, 12101028, 12101802, 12105043, 12105060, 12105070, 12105210, 12107100, 12107200, 12300703, 12300705, 12304400, 12304500, 12400401, 12400403, 12400500, 12400523, 12400524, 12400525, 12400566, 12400567, 12400591, 12400624, 12400650, 12400658, 12400701, 12400708, 12400732, 12400840, 12400900, 12400901, 12410652, 12410657, 12410662, 12410668, 12410676, 12410701, 12410703, 12410704, 12410705, 12410706, 12410715, 12410721, 12410731, 12410732, 12410736, 12410738, 12410742, 12410743, 12410750, 12410762, 12410763, 12410785, 12410801, 12410808, 12410830, 12410850, 12414401, 12414500, 12420500, 12500012, 12500013, 12500014, 12500019, 12500051, 12600701, 12604960, 12604970, 12604980, 12700704, 12700705, 12700901, 12700906, 12700908, 12800902, 12800903, 12800904, 12800905, 12906746, 13200103, 13200105, 13200107, 13200121, 13400940, 13400944, 13400950, 13400951, 13400953, 13400980, 13500943, 13500945, 13500949, 13500950, 13500951, 13500952, 13500953, 13500960, 13500965, 13500968, 13500980, 13500994, 13501920, 13501940, 13600942, 13600943, 13600950, 13600951, 13600952, 13600956};
inline constexpr std::array<std::uint32_t, 17> TalkGroupKeys{12101, 12105, 70000, 72100, 72200, 72300, 72400, 72410, 72500, 72600, 72700, 72800, 72900, 73200, 73400, 73500, 73600};

inline char Kind(std::uint32_t v) {
    if (v >= NpcQuestFlags.front() && v <= NpcQuestFlags.back() &&
        std::binary_search(NpcQuestFlags.begin(), NpcQuestFlags.end(), v)) {
        return 'f';
    }
    if (v >= TalkEvents.front() && v <= TalkEvents.back() &&
        std::binary_search(TalkEvents.begin(), TalkEvents.end(), v)) {
        return 'e';
    }
    if (v >= TalkGroupKeys.front() && v <= TalkGroupKeys.back() &&
        std::binary_search(TalkGroupKeys.begin(), TalkGroupKeys.end(), v)) {
        return 'g';
    }
    return 0;
}

inline bool IsFlag(std::uint32_t v) {
    if (v < NpcQuestFlags.front() || v > NpcQuestFlags.back()) {
        return false;
    }
    return std::binary_search(NpcQuestFlags.begin(), NpcQuestFlags.end(), v);
}

inline void Scan(const char* dir, int socket, std::uint16_t vport, const void* data,
                 std::size_t n) {
    static std::atomic<int> lines{0};
    // Proof of life: the first packet of each direction, and a count every 5000.
    static std::atomic<std::uint64_t> packets[2]{};
    const int d = dir[0] == 's' ? 0 : 1;
    const std::uint64_t k = packets[d].fetch_add(1, std::memory_order_relaxed);
    if (k == 0 || (k + 1) % 5000 == 0) {
        LOG_INFO(Lib_Net, "bbport flag watch: {} packet #{} (socket {}, vport {}, len {})", dir,
                 k + 1, socket, vport, n);
    }
    if (data == nullptr || n < 4 || n > 65536 || lines.load(std::memory_order_relaxed) >= 400) {
        return;
    }
    const auto* b = static_cast<const std::uint8_t*>(data);
    std::string hits;
    std::uint32_t first = 0;
    int count = 0;
    for (std::size_t i = 0; i + 4 <= n; ++i) {
        const std::uint32_t le = std::uint32_t{b[i]} | std::uint32_t{b[i + 1]} << 8 |
                                 std::uint32_t{b[i + 2]} << 16 | std::uint32_t{b[i + 3]} << 24;
        const std::uint32_t be = std::uint32_t{b[i + 3]} | std::uint32_t{b[i + 2]} << 8 |
                                 std::uint32_t{b[i + 1]} << 16 | std::uint32_t{b[i]} << 24;
        const char kind_le = le > 9000 ? Kind(le) : 0;
        const char kind_be = kind_le == 0 && be > 9000 ? Kind(be) : 0;
        if (kind_le == 0 && kind_be == 0) {
            continue;
        }
        const std::uint32_t v = kind_le != 0 ? le : be;
        if (count == 0) {
            first = v;
        }
        if (++count <= 8) {
            hits += fmt::format(" {}{}@{}{}", kind_le != 0 ? kind_le : kind_be, v, i,
                                kind_le != 0 ? "" : "be");
        }
    }
    if (count == 0) {
        return;
    }
    static std::mutex mutex;
    static std::set<std::tuple<char, std::uint16_t, std::size_t, std::uint32_t>> seen;
    {
        std::scoped_lock lock{mutex};
        if (!seen.emplace(dir[0], vport, n, first).second) {
            return;
        }
    }
    if (lines.fetch_add(1, std::memory_order_relaxed) >= 400) {
        return;
    }
    std::string head;
    for (std::size_t i = 0; i < std::min<std::size_t>(n, 96); ++i) {
        head += fmt::format("{:02x}", b[i]);
    }
    LOG_INFO(Lib_Net, "bbport flag watch: {} socket {} vport {} len {}: {} hit(s) (f flag, e event, g group){} | {}",
             dir, socket, vport, n, count, hits, head);
}


// The game's event sync (found 2026-10-27 with the scan above): each player's game sends the runs
// of its events to the others, one message per run step, and the other players' copies of the
// same event follow it - so a talk-driven event (Eileen's "first greeting" step 12410801, the
// talk gifts of 9040 / 9100) ran on everyone when one player talked, and ran out there (BBSC "each
// player's own NPC quests"). The message: 31 00 00 00 | 18 00 00 00 | 00 00 00 00 | 01 00 08 00 |
// 00 00 | u32 event id | u16 slot | u16 step | u32 | u32 (e.g. ... 50 23 00 00 22 00 d0 00: event
// 9040 slot 34 = Eileen's marks). A received one for a talk-driven event (TalkEvents, the Hunter's
// Dream's 121xxxxx left out: BBSC's Dream rules) gets an event id no event has (0xFFFFFFFF), so our
// copy keeps waiting for our own talk; the message stays in place (the game's reliable channel
// and its sequence numbers are untouched). SHADPS4_BBPORT_EVENT_FILTER=0 turns it off.
inline bool FilterEnabled() {
    static const bool enabled = [] {
        const char* value = std::getenv("SHADPS4_BBPORT_EVENT_FILTER");
        return value == nullptr || std::string(value) != "0";
    }();
    return enabled;
}

inline void FilterTalkEvents(void* data, std::size_t n) {
    static constexpr std::array<std::uint8_t, 18> Signature{0x31, 0x00, 0x00, 0x00, 0x18, 0x00,
                                                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                            0x01, 0x00, 0x08, 0x00, 0x00, 0x00};
    if (data == nullptr || n < Signature.size() + 8 || !FilterEnabled()) {
        return;
    }
    auto* b = static_cast<std::uint8_t*>(data);
    for (std::size_t i = 0; i + Signature.size() + 8 <= n; ++i) {
        if (b[i] != 0x31 || !std::equal(Signature.begin(), Signature.end(), b + i)) {
            continue;
        }
        std::uint8_t* id = b + i + Signature.size();
        const std::uint32_t event = std::uint32_t{id[0]} | std::uint32_t{id[1]} << 8 |
                                    std::uint32_t{id[2]} << 16 | std::uint32_t{id[3]} << 24;
        const std::uint16_t slot = static_cast<std::uint16_t>(id[4] | id[5] << 8);
        i += Signature.size() + 3;
        if (event / 100000 == 121 || !std::binary_search(TalkEvents.begin(), TalkEvents.end(),
                                                         event)) {
            continue;
        }
        id[0] = id[1] = id[2] = id[3] = 0xFF;
        static std::mutex mutex;
        static std::set<std::uint64_t> logged;
        bool first = false;
        {
            std::scoped_lock lock{mutex};
            first = logged.size() < 512 &&
                    logged.insert(std::uint64_t{event} << 16 | slot).second;
        }
        if (first) {
            LOG_INFO(Lib_Net, "bbport event filter: the other player's run of talk-driven event {} "
                              "(slot {}) not followed here",
                     event, slot);
        }
    }
}

} // namespace Libraries::Net::FlagWatch
