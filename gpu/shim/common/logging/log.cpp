// bbport: see log.h.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
#include <ctime>
#include <mutex>
#include <string>
#include <filesystem>
#ifdef _WIN32
#include <windows.h>
#endif
#include "common/logging/log.h"

namespace Common::Log {
static Level threshold() {
    static const Level level = [] {
        const char* v = std::getenv("BB_GPU_LOG");
        if (!v) return Level::warn;
        static const char* names[] = {"trace", "debug", "info", "warning", "error", "critical"};
        for (int i = 0; i < 6; ++i)
            if (!std::strcmp(v, names[i])) return Level(i);
        return Level::warn;
    }();
    return level;
}
bool ShouldLog(Level level) { return level >= threshold(); }
bool ShouldLogClass(std::string_view log_class, Level level) {
    if (level >= threshold()) return true;
    static const std::string classes = [] {
        const char* v = std::getenv("BB_GPU_LOG_CLASSES");
        if (v) return std::string(v);
        const char* coop = std::getenv("BB_COOP");
        return std::string(coop && std::strcmp(coop, "1") == 0
            ? "Lib.NpSignaling,Lib.NpMatching2" : "");
    }();
    if (classes.empty() || level < Level::info) return false;
    size_t pos = 0;
    while (pos <= classes.size()) {
        size_t end = classes.find(',', pos);
        if (end == std::string::npos) end = classes.size();
        if (classes.compare(pos, end - pos, log_class) == 0 && end - pos == log_class.size()) return true;
        pos = end + 1;
    }
    return false;
}
void Write(std::string_view log_class, Level level, const char* file, int line, const char* function,
           std::string&& message) {
    static std::mutex mutex;
    // BB_GPU_LOG_FILE=<path>: the log also goes there (the launcher does not always keep stderr).
    static std::FILE* log_file = [] {
        const char* v = std::getenv("BB_GPU_LOG_FILE");
        if (v && *v) return std::fopen(v, "a");
#ifdef _WIN32
        const char* coop = std::getenv("BB_COOP");
        if (coop && std::strcmp(coop, "1") == 0) {
            const wchar_t* user = _wgetenv(L"BB_USER_DIR");
            if (user && *user) {
                std::error_code ec;
                const auto dir = std::filesystem::path(user) / L"log";
                std::filesystem::create_directories(dir, ec);
                if (!ec) {
                    SYSTEMTIME t{}; GetLocalTime(&t);
                    wchar_t name[96]{};
                    swprintf_s(name, L"bbnet-%04u%02u%02u-%02u%02u%02u-%lu.log",
                               t.wYear, t.wMonth, t.wDay, t.wHour, t.wMinute, t.wSecond,
                               GetCurrentProcessId());
                    return _wfopen((dir / name).c_str(), L"a");
                }
            }
        }
#endif
        return static_cast<std::FILE*>(nullptr);
    }();
    static const char* names[] = {"Trace", "Debug", "Info", "Warning", "Error", "Critical"};
    const char* base = std::strrchr(file, '/');
    std::scoped_lock lock{mutex};
    const auto now = std::chrono::system_clock::now();
    const std::time_t secs = std::chrono::system_clock::to_time_t(now);
    std::tm local{};
#ifdef _WIN32
    localtime_s(&local, &secs);
#else
    localtime_r(&secs, &local);
#endif
    const int ms = int(std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count() % 1000);
    std::fprintf(stderr, "[%02d:%02d:%02d.%03d] GPU [%.*s] <%s> %s:%d %s: %s\n", local.tm_hour, local.tm_min,
                 local.tm_sec, ms, int(log_class.size()), log_class.data(), names[int(level)], base ? base + 1 : file, line, function, message.c_str());
    if (log_file) {
        std::fprintf(log_file, "[%02d:%02d:%02d.%03d] GPU [%.*s] <%s> %s:%d %s: %s\n", local.tm_hour, local.tm_min,
                     local.tm_sec, ms, int(log_class.size()), log_class.data(), names[int(level)], base ? base + 1 : file, line, function, message.c_str());
        std::fflush(log_file);
    }
}
} // namespace Common::Log
