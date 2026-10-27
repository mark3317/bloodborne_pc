// bbport: see log.h.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
#include <ctime>
#include <mutex>
#include <string>
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
        return std::string(v ? v : "");
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
        return v && *v ? std::fopen(v, "a") : nullptr;
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
