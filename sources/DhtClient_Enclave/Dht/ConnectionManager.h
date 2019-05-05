#pragma once

#include <DecentApi/Common/Tools/SharedCachingQueue.h>
#include <DecentApi/Common/Net/SecureConnectionPoolBase.h>

namespace Decent
{
	namespace Ra
	{
		class States;
	}

	namespace MbedTlsObj
	{
		class Session;
	}

	namespace DhtClient
	{

		class ConnectionManager
		{
		public:
			ConnectionManager(size_t cacheSize);

			virtual ~ConnectionManager();

			void InitConnectionPoolPtr(void* ptr);

			virtual Net::CntPair GetNew(const uint64_t& addr, Ra::States& state);

			virtual Net::CntPair GetAny(Ra::States& state);

		private:
			Tools::SharedCachingQueue<uint64_t, MbedTlsObj::Session> m_sessionCache;
			void* m_cntPoolPtr;
		};
	}
}
