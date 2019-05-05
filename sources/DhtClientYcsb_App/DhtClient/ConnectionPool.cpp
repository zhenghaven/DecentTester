#include "ConnectionPool.h"

#include <DecentApi/Common/Common.h>

#include <DecentApi/CommonApp/Net/TCPConnection.h>
#include <DecentApi/CommonApp/Tools/ConfigManager.h>

#include "AppNames.h"

using namespace Decent;
using namespace Decent::DhtClient;
using namespace Decent::Tools;

ConnectionPool::ConnectionPool(size_t maxInCnt, size_t maxOutCnt, const ConfigManager& cfgMgr) : 
	Net::ConnectionPool<uint64_t>(maxInCnt, maxOutCnt), 
	m_firstNodeAddr(Net::TCPConnection::CombineIpAndPort(
		Net::TCPConnection::GetIpAddressFromStr(cfgMgr.GetItem(AppNames::sk_decentDHT).GetAddr()), 
		cfgMgr.GetItem(AppNames::sk_decentDHT).GetPort())
	)
{}

ConnectionPool::~ConnectionPool()
{
}

std::unique_ptr<Net::ConnectionBase> ConnectionPool::GetNew(const uint64_t & addr)
{
	return std::make_unique<Net::TCPConnection>(addr);
}

std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> ConnectionPool::GetAnyDhtNode()
{
	return GetAny(m_firstNodeAddr);
}

std::shared_ptr<ConnectionPool> ConnectionPool::GetSharedPtr()
{
	return shared_from_this();
}
