#include <memory>

//#include <DecentApi/Common/Common.h>

#include <DecentApi/Common/Net/ConnectionBase.h>
#include <DecentApi/Common/Net/CntPoolConnection.h>

#include "../Common_App/DhtClient/ConnectionPool.h"
#include "../Common_App/DhtClient/RequestCategory.h"

using namespace Decent;
using namespace Decent::DhtClient;

extern "C" void* ocall_dht_client_cnt_pool_get_dht_any(void* cnt_pool_ptr, uint64_t* address)
{
	if (!cnt_pool_ptr)
	{
		return nullptr;
	}

	ConnectionPool& cntPoolRef = *static_cast<ConnectionPool*>(cnt_pool_ptr);

	try
	{
		std::pair<std::unique_ptr<Net::ConnectionBase>, uint64_t> cntPair = cntPoolRef.GetAnyDhtNode();

		if (!cntPair.first)
		{
			return nullptr;
		}

#ifndef DHT_USER_TEST
		cntPair.first->SendContainer(Dht::RequestCategory::sk_fromApp);
#else
		cntPair.first->SendContainer(Dht::RequestCategory::sk_fromUser);
#endif // DHT_USER_TEST

		if (address)
		{
			*address = cntPair.second;
		}

		return new Net::CntPoolConnection<uint64_t>(cntPair.second, std::move(cntPair.first), cntPoolRef.GetSharedPtr());
	}
	catch (const std::exception& e)
	{
		(void)e;
		//PRINT_W("Failed to establish connection. (Err Msg: %s)", e.what());
		return nullptr;
	}
}

extern "C" void* ocall_dht_client_cnt_pool_get_dht(void* cnt_pool_ptr, uint64_t address)
{
	if (!cnt_pool_ptr)
	{
		return nullptr;
	}

	ConnectionPool& cntPoolRef = *static_cast<ConnectionPool*>(cnt_pool_ptr);

	try
	{
		std::unique_ptr<Net::ConnectionBase> cnt = cntPoolRef.Get(address);

		if (!cnt)
		{
			return nullptr;
		}

#ifndef DHT_USER_TEST
		cnt->SendContainer(Dht::RequestCategory::sk_fromApp);
#else
		cnt->SendContainer(Dht::RequestCategory::sk_fromUser);
#endif // DHT_USER_TEST

		return new Net::CntPoolConnection<uint64_t>(address, std::move(cnt), cntPoolRef.GetSharedPtr());
	}
	catch (const std::exception& e)
	{
		(void)e;
		//PRINT_W("Failed to establish connection. (Err Msg: %s)", e.what());
		return nullptr;
	}
}

extern "C" void* ocall_dht_client_malloc(size_t size)
{
	return (new uint8_t[size]);
}
