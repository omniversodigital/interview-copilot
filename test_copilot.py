import urllib.request
import json
import asyncio
import websockets

def test_endpoints():
    # 1. Test GET /
    req = urllib.request.urlopen('http://127.0.0.1:8888/')
    assert req.status == 200
    html = req.read().decode('utf-8')
    assert 'SOVEREIGN CO-PILOT' in html
    print('PASS: GET / (HTML served properly)')

    # 2. Test GET /api/topics
    req = urllib.request.urlopen('http://127.0.0.1:8888/api/topics')
    assert req.status == 200
    topics = json.loads(req.read().decode('utf-8'))
    assert len(topics) >= 5
    print(f'PASS: GET /api/topics ({len(topics)} topics loaded)')

    # 3. Test POST /api/query
    data = json.dumps({'query': 'How do you handle policy latency in distributed microservices?'}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8888/api/query', data=data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    assert res.status == 200
    payload = json.loads(res.read().decode('utf-8'))
    assert payload['matched'] is True
    title = payload['topic']['title']
    conf = payload['confidence']
    print(f'PASS: POST /api/query -> Matched: {title} ({conf}%)')

async def test_ws():
    async with websockets.connect('ws://127.0.0.1:8888/ws/transcribe') as ws:
        init_msg = json.loads(await ws.recv())
        assert init_msg['type'] == 'connected'
        print('PASS: WebSocket connected successfully')
        
        # Send speech message
        await ws.send(json.dumps({
            'action': 'speech',
            'text': 'What happens when UAV swarm drones face communication loss or packet loss?',
            'is_final': True
        }))
        res = json.loads(await ws.recv())
        assert res['type'] == 'result'
        ws_title = res['data']['topic']['title']
        assert 'Autonomous UAV' in ws_title
        print(f'PASS: WebSocket speech response -> {ws_title}')

if __name__ == '__main__':
    test_endpoints()
    asyncio.run(test_ws())
    print('\nALL SYSTEM CHECKS PASSED: 100% OPERATIONAL!')
