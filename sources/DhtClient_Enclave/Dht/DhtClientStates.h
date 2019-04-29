#pragma once

#include <DecentApi/DecentAppEnclave/AppStates.h>

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionPool;

		class States : public Ra::AppStates
		{
		public:
			States(Ra::AppCertContainer & certCntnr, Ra::KeyContainer & keyCntnr, Ra::WhiteList::DecentServer & serverWl, GetLoadedWlFunc getLoadedFunc, ConnectionPool& cntPool) :
				AppStates(certCntnr, keyCntnr, serverWl, getLoadedFunc),
				m_cntPool(cntPool)
			{}

			virtual ~States()
			{}

			const ConnectionPool& GetConnectionPool() const
			{
				return m_cntPool;
			}

			ConnectionPool& GetConnectionPool()
			{
				return m_cntPool;
			}

		private:
			ConnectionPool& m_cntPool;
		};
	}
}
