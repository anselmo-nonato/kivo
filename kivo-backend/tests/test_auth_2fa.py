import asyncio
import httpx
import pyotp

BASE_URL = 'http://localhost:8000/api/v1'

async def run_auth_2fa_test_suite():
    print('\n==========================================')
    print('INICIANDO TESTES DE AUTENTICAÇÃO & 2FA')
    print('==========================================\n')
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Teste de Registro
        email = f'anselmo.teste.{int(asyncio.get_event_loop().time()*1000)}@kivo.app'
        password = 'SenhaSegura123#Kivo'
        full_name = 'Anselmo Nonato Teste'
        
        print(f'1. Testando /auth/register para {email}...')
        res = await client.post('/auth/register', json={
            'email': email,
            'password': password,
            'full_name': full_name,
            'initial_workspace_name': 'Finanças Anselmo & Família'
        })
        assert res.status_code == 201, f'Falha no registro: {res.text}'
        data = res.json()
        access_token = data['access_token']
        refresh_token = data['refresh_token']
        user = data['user']
        
        assert user['email'] == email
        assert user['mfa_enabled'] is False
        assert len(user['workspaces']) == 1
        print('  ✓ Registro com sucesso! Workspace Solo criado.')

        # 2. Teste de /auth/me
        print('2. Testando rota protegida /auth/me com Access Token...')
        res = await client.get('/auth/me', headers={'Authorization': f'Bearer {access_token}'})
        assert res.status_code == 200
        assert res.json()['id'] == user['id']
        print('  ✓ Rota protegida acessada com sucesso.')

        # 3. Teste de /auth/2fa/setup
        print('3. Testando /auth/2fa/setup...')
        res = await client.post('/auth/2fa/setup', headers={'Authorization': f'Bearer {access_token}'})
        assert res.status_code == 200
        setup_data = res.json()
        secret = setup_data['secret']
        qr_code = setup_data['qr_code_base64']
        backup_codes = setup_data['backup_codes']
        
        assert len(secret) == 32
        assert qr_code.startswith('data:image/png;base64,')
        assert len(backup_codes) == 8
        print(f'  ✓ Segredo TOTP gerado: {secret[:6]}... e 8 códigos de backup gerados.')

        # 4. Teste de /auth/2fa/enable com código real
        print('4. Testando /auth/2fa/enable com código TOTP...')
        totp = pyotp.TOTP(secret)
        current_code = totp.now()
        
        res = await client.post('/auth/2fa/enable', json={'code': current_code}, headers={'Authorization': f'Bearer {access_token}'})
        assert res.status_code == 200
        assert res.json()['mfa_enabled'] is True
        print('  ✓ 2FA ativado com sucesso após validação de 6 dígitos!')

        # 5. Teste de Login com 2FA Ativo (Etapa 1)
        print('5. Testando /auth/login com 2FA ativado (Etapa 1)...')
        res = await client.post('/auth/login', json={'email': email, 'password': password})
        assert res.status_code == 200
        login_step1 = res.json()
        assert login_step1['mfa_required'] is True
        mfa_token = login_step1['mfa_token']
        print('  ✓ Login retornou mfa_required=True e mfa_token de desafio.')

        # 6. Teste de /auth/2fa/verify com código inválido
        print('6. Testando /auth/2fa/verify com código inválido...')
        res = await client.post('/auth/2fa/verify', json={'mfa_token': mfa_token, 'code': '000000'})
        assert res.status_code == 401
        print('  ✓ Código inválido rejeitado com 401 Unauthorized.')

        # 7. Teste de /auth/2fa/verify com código TOTP válido (Etapa 2)
        print('7. Testando /auth/2fa/verify com código TOTP válido (Etapa 2)...')
        valid_totp_code = totp.now()
        res = await client.post('/auth/2fa/verify', json={'mfa_token': mfa_token, 'code': valid_totp_code})
        assert res.status_code == 200
        step2_tokens = res.json()
        assert 'access_token' in step2_tokens
        assert step2_tokens['user']['mfa_enabled'] is True
        print('  ✓ Login concluído com sucesso via TOTP!')

        # 8. Teste de Login usando Código de Backup
        print('8. Testando Login via Código de Backup (Recuperação de Emergência)...')
        res = await client.post('/auth/login', json={'email': email, 'password': password})
        mfa_token_backup = res.json()['mfa_token']
        first_backup_code = backup_codes[0]
        
        res = await client.post('/auth/2fa/verify', json={'mfa_token': mfa_token_backup, 'code': first_backup_code})
        assert res.status_code == 200
        print(f'  ✓ Login realizado com sucesso usando Backup Code ({first_backup_code})!')

        # 9. Teste de Reuso do mesmo Código de Backup (Deve falhar)
        print('9. Testando reuso do mesmo Código de Backup (Uso Único)...')
        res = await client.post('/auth/login', json={'email': email, 'password': password})
        mfa_token_reuse = res.json()['mfa_token']
        
        res = await client.post('/auth/2fa/verify', json={'mfa_token': mfa_token_reuse, 'code': first_backup_code})
        assert res.status_code == 401
        print('  ✓ Reuso de código de backup já utilizado foi bloqueado com sucesso!')

        # 10. Teste de /auth/refresh
        print('10. Testando renovação de token via /auth/refresh...')
        res = await client.post('/auth/refresh', params={'refresh_token': refresh_token})
        assert res.status_code == 200
        assert 'access_token' in res.json()
        print('  ✓ Access Token renovado com sucesso.')

        # 11. Teste de Desativação do 2FA
        print('11. Testando desativação do 2FA (/auth/2fa/disable)...')
        res = await client.post('/auth/2fa/disable', json={
            'password': password,
            'code': totp.now()
        }, headers={'Authorization': f'Bearer {access_token}'})
        assert res.status_code == 200
        assert res.json()['mfa_enabled'] is False
        print('  ✓ 2FA desativado com sucesso mediante senha e código.')

        # 12. Teste de Dispositivo Confiável (Remember Device 30 Dias)
        print('12. Reativando 2FA e testando "Lembrar este dispositivo por 30 dias"...')
        res_setup2 = await client.post('/auth/2fa/setup', headers={'Authorization': f'Bearer {access_token}'})
        secret2 = res_setup2.json()['secret']
        totp2 = pyotp.TOTP(secret2)
        await client.post('/auth/2fa/enable', json={'code': totp2.now()}, headers={'Authorization': f'Bearer {access_token}'})

        # Login Etapa 1
        res_log1 = await client.post('/auth/login', json={'email': email, 'password': password})
        mfa_tok = res_log1.json()['mfa_token']

        # Login Etapa 2 com remember_device = True
        res_ver_dev = await client.post('/auth/2fa/verify', json={
            'mfa_token': mfa_tok,
            'code': totp2.now(),
            'remember_device': True,
            'device_name': 'Chrome no Windows 11'
        })
        assert res_ver_dev.status_code == 200
        trusted_dev_token = res_ver_dev.json()['trusted_device_token']
        assert trusted_dev_token is not None
        print(f'  ✓ 2FA validado com Lembrar Dispositivo! Token emitido: {trusted_dev_token[:12]}...')

        # 13. Teste de Login subsequente usando o Trusted Device Token (deve pular o 2FA!)
        print('13. Testando Login subsequente com Trusted Device Token (Pulo do 2FA)...')
        res_direct = await client.post('/auth/login', json={
            'email': email,
            'password': password,
            'trusted_device_token': trusted_dev_token
        })
        assert res_direct.status_code == 200
        direct_data = res_direct.json()
        assert 'access_token' in direct_data
        assert direct_data.get('mfa_required') is not True
        print('  ✓ SUCESSO: Login com Trusted Device pulou o desafio 2FA e emitiu sessão válida diretamente!')

        # 14. Teste de Listagem e Revogação de Dispositivos Confiáveis
        print('14. Testando listagem e revogação de dispositivos confiáveis...')
        res_dev_list = await client.get('/auth/trusted-devices', headers={'Authorization': f'Bearer {direct_data["access_token"]}'})
        assert res_dev_list.status_code == 200
        assert len(res_dev_list.json()) >= 1

        await client.delete('/auth/trusted-devices', headers={'Authorization': f'Bearer {direct_data["access_token"]}'})
        res_after_revoke = await client.post('/auth/login', json={
            'email': email,
            'password': password,
            'trusted_device_token': trusted_dev_token
        })
        assert res_after_revoke.status_code == 200
        assert res_after_revoke.json()['mfa_required'] is True
        print('  ✓ Dispositivos revogados com sucesso! Próximo login exigiu 2FA normalmente.')

    print('\n==========================================')
    print('✅ TODOS OS TESTES DE AUTH, 2FA E DISPOSITIVOS CONFIÁVEIS PASSARAM COM 100% DE SUCESSO!')
    print('==========================================\n')

if __name__ == '__main__':
    asyncio.run(run_auth_2fa_test_suite())
