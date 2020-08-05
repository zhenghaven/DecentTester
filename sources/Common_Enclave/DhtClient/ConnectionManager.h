#pragma once

#include<mutex>
#include<map>
#include<vector>

#include <DecentApi/Common/Tools/SharedCachingQueue.h>
#include <DecentApi/Common/Net/SecureConnectionPoolBase.h>

#if !defined(DECENT_DHT_NAIVE_RA_VER) && defined(ENCLAVE_PLATFORM_SGX)
//#	define DECENT_DHT_NAIVE_RA_VER
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
			ConnectionManager(size_t cacheSize, int64_t opCountMax);

			virtual ~ConnectionManager();

			/**
			 * \brief	Re-initializes the maximum number of operation count. Note: opCountMax is not thread-
			 * 			safe, thus, do not call this function after the initialization phase.
			 *
			 * \param	opCountMax	The operation count maximum.
			 */
			void InitOpCountMax(int64_t opCountMax, const std::vector<uint64_t>& knownAddr);

			virtual Net::CntPair GetNew(void* cntPoolPtr, const uint64_t& addr, States& state);

			virtual Net::CntPair GetAny(void* cntPoolPtr, States& state);

		private:
#ifdef DECENT_DHT_NAIVE_RA_VER
			Tools::SharedCachingQueue<uint64_t, const Sgx::RaClientSession> m_sessionCache;
#else
			Tools::SharedCachingQueue<uint64_t, MbedTlsObj::Session> m_sessionCache;
#endif

			void CheckOpCount(const uint64_t addr);

			int64_t m_opCountMax;
			std::mutex m_opCountMutex;
			uint64_t m_opCount;
			std::map<uint64_t, uint64_t> m_idvOpCount;
		};
	}
}
