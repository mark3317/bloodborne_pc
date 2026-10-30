// Real native UDP transport, codec, readiness, peek and delivery under diagnostic load.
#include "core/net/p2p_codec.h"
#include "core/net/p2p_transport.h"
#include <array>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <thread>
using namespace Core::Net;
using namespace Core::Net::P2P;
using namespace std::chrono_literals;

static void Receive(DatagramSocket& socket, const std::array<u8,64>& expected, bool peek=false) {
    const auto until=Clock::now()+2s;
    std::array<u8,64> payload{};
    for (;;) {
        const auto result=socket.RecvFrom(payload,peek,nullptr,nullptr);
        if (result.error==Host::Error::Ok) {
            assert(result.bytes==payload.size() && payload==expected);
            return;
        }
        assert(result.error==Host::Error::WouldBlock && Clock::now()<until);
        std::this_thread::sleep_for(1ms);
    }
}

int main() {
    assert(Host::Initialize());
    Host::Error error{};
    auto a=Transport::Create(AF_INET,Endpoint::IPv4("127.0.0.1",0),
        std::make_unique<FramingCodec>(std::make_shared<Keyring>()),TransportConfig{},&error);
    assert(a && error==Host::Error::Ok);
    auto b=Transport::Create(AF_INET,Endpoint::IPv4("127.0.0.1",0),
        std::make_unique<FramingCodec>(std::make_shared<Keyring>()),TransportConfig{},&error);
    assert(b && error==Host::Error::Ok);
    auto sa=a->CreateDatagram(), sb=b->CreateDatagram();
    assert(sa->Bind(100)==Host::Error::Ok && sb->Bind(200)==Host::Error::Ok);
    const auto ea=Endpoint::IPv4("127.0.0.1",a->BoundPort());
    const auto eb=Endpoint::IPv4("127.0.0.1",b->BoundPort());
    long long worst_us=0;
    for (int i=0;i<270;++i) {
        std::array<u8,64> payload{};
        payload[0]=static_cast<u8>(i); payload[1]=static_cast<u8>(i>>8);
        const auto start=Clock::now();
        assert(sa->SendTo(payload,&eb,200).error==Host::Error::Ok);
        Receive(*sb,payload,true); // peek must retain the same packet
        Receive(*sb,payload);
        assert(sb->SendTo(payload,&ea,100).error==Host::Error::Ok);
        Receive(*sa,payload);
        worst_us=std::max(worst_us,std::chrono::duration_cast<std::chrono::microseconds>(Clock::now()-start).count());
        std::this_thread::sleep_for(20ms); // cross the diagnostic flush boundary
    }
    std::printf("PASS: 540 real UDP deliveries, native framing/readiness/peek, diagnostic flush; worst round trip %lld us\n",worst_us);
}
