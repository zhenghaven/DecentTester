#pragma once

#include <vector>

#include <DecentApi/Common/general_key_types.h>
#include <DecentApi/DecentAppEnclave/AppStates.h>

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionManager;

		struct CachedAttributeList
		{
			std::vector<uint8_t> m_list;
			general_secp256r1_signature_t m_sign;
			std::string m_certPem;
		};

		class States : public Ra::AppStates
		{
		public:
			States(Ra::AppCertContainer & certCntnr, Ra::KeyContainer & keyCntnr, Ra::WhiteList::DecentServer & serverWl, GetLoadedWlFunc getLoadedFunc, ConnectionManager& cntMgr) :
				AppStates(certCntnr, keyCntnr, serverWl, getLoadedFunc),
				m_cntMgr(cntMgr),
				m_attrCache()
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

			const std::shared_ptr<CachedAttributeList>& GetAttributeCache() const
			{
				return m_attrCache;
			}

			std::shared_ptr<CachedAttributeList>& GetAttributeCache()
			{
				return m_attrCache;
			}

		private:
			ConnectionManager& m_cntMgr;

			std::shared_ptr<CachedAttributeList> m_attrCache;
		};
	}
}
