#include "ConnectionPool.h"

#include <DecentApi/Common/Common.h>
#include <algorithm>

#include <DecentApi/Common/Common.h>

#include <DecentApi/CommonApp/Net/TCPConnection.h>
#include <DecentApi/CommonApp/AppConfig/EnclaveList.h>

#include "AppNames.h"

using namespace Decent;
using namespace Decent::DhtClient;
using namespace Decent::Tools;

namespace
{
	static uint64_t GetFirstKnownAddress(const AppConfig::EnclaveList& cfgEnclaveList)
	{
		return Net::TCPConnection::CombineIpAndPort(
			Net::TCPConnection::GetIpAddressFromStr(cfgEnclaveList.GetItem(AppNames::sk_decentDHT).GetAddr()),
			57756U);
	}

	static uint64_t GetAddressInConfig(const AppConfig::EnclaveList& cfgEnclaveList)
	{
		return Net::TCPConnection::CombineIpAndPort(
			Net::TCPConnection::GetIpAddressFromStr(cfgEnclaveList.GetItem(AppNames::sk_decentDHT).GetAddr()),
			cfgEnclaveList.GetItem(AppNames::sk_decentDHT).GetPort());
	}
}

ConnectionPool::ConnectionPool(size_t maxInCnt, size_t maxOutCnt, const AppConfig::EnclaveList& cfgEnclaveList) :
	Net::ConnectionPool<uint64_t>(maxInCnt, maxOutCnt), 
	m_rd(),
	m_randGen(m_rd()),
	m_knownNodeAddr(),
	m_uniDist()
{
	for (uint64_t a = GetFirstKnownAddress(cfgEnclaveList); a <= GetAddressInConfig(cfgEnclaveList); ++a)
	{
		m_knownNodeAddr.push_back(a);
	}

	PRINT_I("Test with %llu DHT nodes.", m_knownNodeAddr.size());

	m_uniDist = std::make_unique<std::uniform_int_distribution<size_t> >(0, m_knownNodeAddr.size() - 1);
}

ConnectionPool::~ConnectionPool()
{
}

std::unique_ptr<Net::ConnectionBase> ConnectionPool::GetNew(const uint64_t & addr)
{
	return std::make_unique<Net::TCPConnection>(addr);
}

std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> ConnectionPool::GetAnyDhtNode()
{
	uint64_t addr = m_knownNodeAddr[(*m_uniDist)(m_randGen)];
	return std::make_pair(Get(addr), addr);
}

std::shared_ptr<ConnectionPool> ConnectionPool::GetSharedPtr()
{
	return shared_from_this();
}

const std::vector<uint64_t>& ConnectionPool::GetKnownNodeAddr() const
{
	return m_knownNodeAddr;
}
