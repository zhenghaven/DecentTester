#pragma once

#include <DecentApi/Common/Tools/SharedCachingQueue.h>
#include <DecentApi/Common/Net/SecureConnectionPoolBase.h>

#if !defined(DECENT_DHT_NAIVE_RA_VER) && defined(ENCLAVE_PLATFORM_SGX)
#	define DECENT_DHT_NAIVE_RA_VER
#endif // !defined(DECENT_DHT_NAIVE_RA_VER) && defined(ENCLAVE_PLATFORM_SGX)

#ifdef DECENT_DHT_NAIVE_RA_VER
#	include <DecentApi/Common/SGX/RaTicket.h>
#endif

namespace Decent
{
	namespace MbedTlsObj
	{
		class Session;
	}

	namespace DhtClient
	{
		class States;

		class ConnectionManager
		{
		public:
			ConnectionManager(size_t cacheSize);

			virtual ~ConnectionManager();

			virtual Net::CntPair GetNew(void* cntPoolPtr, const uint64_t& addr, States& state);

			virtual Net::CntPair GetAny(void* cntPoolPtr, States& state);

		private:
#ifdef DECENT_DHT_NAIVE_RA_VER
			Tools::SharedCachingQueue<uint64_t, const Sgx::RaClientSession> m_sessionCache;
#else
			Tools::SharedCachingQueue<uint64_t, MbedTlsObj::Session> m_sessionCache;
#endif
		};
	}
}
