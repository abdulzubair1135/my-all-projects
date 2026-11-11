class_name NetworkMatchManagerNode
extends Node

const DEFAULT_SERVER_PORT = 7777
const MAX_PLAYERS = 2

# Network signals
signal connection_succeeded()
signal connection_failed()
signal player_connected(peer_id: int)
signal match_started(map_seed: int)
signal opponent_army_received(army_data: Dictionary)
signal game_state_synced(snapshot: Dictionary)

var peer: ENetMultiplayerPeer
var is_server: bool = false
var connected_players: Dictionary = {}
var local_player_army: Dictionary = {}
var remote_player_army: Dictionary = {}

func _get_mp() -> MultiplayerAPI:
	if is_inside_tree():
		return multiplayer
	var ml = Engine.get_main_loop()
	if ml and "root" in ml and ml.root:
		return ml.root.get_multiplayer()
	return null

func host_match(port: int = DEFAULT_SERVER_PORT) -> bool:
	peer = ENetMultiplayerPeer.new()
	var error = peer.create_server(port, MAX_PLAYERS)
	if error != OK:
		push_error("Failed to host server on port %d: %s" % [port, error])
		return false
		
	var mp = _get_mp()
	if mp:
		mp.multiplayer_peer = peer
		mp.peer_connected.connect(_on_peer_connected)
		mp.peer_disconnected.connect(_on_peer_disconnected)
	is_server = true
	print("[NETWORK] Server listening on port %d" % port)
	return true

func join_match(address: String = "127.0.0.1", port: int = DEFAULT_SERVER_PORT) -> bool:
	peer = ENetMultiplayerPeer.new()
	var error = peer.create_client(address, port)
	if error != OK:
		push_error("Failed to connect to %s:%d: %s" % [address, port, error])
		return false
		
	var mp = _get_mp()
	if mp:
		mp.multiplayer_peer = peer
		mp.connected_to_server.connect(_on_connected_to_server)
		mp.connection_failed.connect(_on_connection_failed)
	is_server = false
	print("[NETWORK] Connecting to server at %s:%d..." % [address, port])
	return true

func _on_peer_connected(id: int) -> void:
	print("[NETWORK] Peer %d connected." % id)
	player_connected.emit(id)
	if is_server and multiplayer.get_peers().size() >= 1:
		# Send server start RPC
		rpc("rpc_start_match", randi())

func _on_peer_disconnected(id: int) -> void:
	print("[NETWORK] Peer %d disconnected." % id)

func _on_connected_to_server() -> void:
	print("[NETWORK] Successfully connected to game server.")
	connection_succeeded.emit()
	if not local_player_army.is_empty():
		rpc_id(1, "rpc_submit_army", local_player_army)

func _on_connection_failed() -> void:
	push_error("[NETWORK] Connection attempt failed.")
	connection_failed.emit()

@rpc("any_peer", "call_remote", "reliable")
func rpc_submit_army(army_data: Dictionary) -> void:
	var sender_id = multiplayer.get_remote_sender_id()
	print("[NETWORK] Received army submission from peer %d." % sender_id)
	
	# Server validates army before accepting
	if is_server:
		var army = ArmyLoadout.deserialize(army_data)
		var val = army.validate_army(1000, 300)
		if not val.is_valid:
			print("[NETWORK ANTI-CHEAT] Rejected illegal army from peer %d: %s" % [sender_id, val.errors[0]])
			return
		
		# Broadcast to other client
		for peer_id in multiplayer.get_peers():
			if peer_id != sender_id:
				rpc_id(peer_id, "rpc_receive_opponent_army", army_data)

@rpc("authority", "call_remote", "reliable")
func rpc_receive_opponent_army(army_data: Dictionary) -> void:
	remote_player_army = army_data
	opponent_army_received.emit(army_data)

@rpc("authority", "call_remote", "reliable")
func rpc_start_match(seed_val: int) -> void:
	seed(seed_val)
	match_started.emit(seed_val)

func disconnect_match() -> void:
	if peer:
		peer.close()
		var mp = _get_mp()
		if mp and mp.multiplayer_peer == peer:
			mp.multiplayer_peer = null
		is_server = false
