#pragma once

#include <DecentApi/DecentAppEnclave/AppStates.h>

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionManager;

		class States : public Ra::AppStates
		{
		public:
			States(Ra::AppCertContainer & certCntnr, Ra::KeyContainer & keyCntnr, Ra::WhiteList::DecentServer & serverWl, GetLoadedWlFunc getLoadedFunc, ConnectionManager& cntMgr) :
				AppStates(certCntnr, keyCntnr, serverWl, getLoadedFunc),
				m_cntMgr(cntMgr)
			{}

			virtual ~States()
			{}

			const ConnectionManager& GetConnectionMgr() const
			{
				return m_cntMgr;
			}

			ConnectionManager& GetConnectionMgr()
			{
				return m_cntMgr;
			}

		private:
			ConnectionManager& m_cntMgr;
		};
	}
}
