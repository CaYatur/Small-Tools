package com.example.bluetoothwatch

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class MainActivity : AppCompatActivity() {
    private var bluetoothAdapter: BluetoothAdapter? = null
    private val devices = mutableListOf<BluetoothDevice>()
    private lateinit var adapter: DeviceAdapter

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { perms ->
        // ignore detailed handling here; scan will fail silently if denied
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()

        adapter = DeviceAdapter(devices, object : DeviceActions {
            override fun pair(device: BluetoothDevice) {
                device.createBond()
            }

            override fun unpair(device: BluetoothDevice) {
                try {
                    val method = device.javaClass.getMethod("removeBond")
                    method.invoke(device)
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        })

        val rv = findViewById<RecyclerView>(R.id.rvDevices)
        rv.layoutManager = LinearLayoutManager(this)
        rv.adapter = adapter

        findViewById<Button>(R.id.btnScan).setOnClickListener {
            ensurePermissionsThenScan()
        }

        // broadcast receiver for found devices and bond state changes
        val filter = IntentFilter().apply {
            addAction(BluetoothDevice.ACTION_FOUND)
            addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)
            addAction(BluetoothDevice.ACTION_BOND_STATE_CHANGED)
        }
        registerReceiver(receiver, filter)
    }

    override fun onDestroy() {
        super.onDestroy()
        try { unregisterReceiver(receiver) } catch (_: Exception) {}
    }

    private fun ensurePermissionsThenScan() {
        val req = mutableListOf<String>()
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) != PackageManager.PERMISSION_GRANTED) {
            req.add(Manifest.permission.BLUETOOTH_SCAN)
        }
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
            req.add(Manifest.permission.BLUETOOTH_CONNECT)
        }
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            req.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }
        if (req.isNotEmpty()) {
            permissionLauncher.launch(req.toTypedArray())
        }
        startDiscovery()
    }

    private fun startDiscovery() {
        bluetoothAdapter?.let { bt ->
            if (bt.isDiscovering) bt.cancelDiscovery()
            bt.startDiscovery()
            // clear previous
            devices.clear()
            adapter.notifyDataSetChanged()
        }
    }

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent == null) return
            when (intent.action) {
                BluetoothDevice.ACTION_FOUND -> {
                    val device: BluetoothDevice? = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                    device?.let {
                        if (!devices.any { d -> d.address == it.address }) {
                            devices.add(it)
                            adapter.notifyItemInserted(devices.size - 1)
                        }
                    }
                }
                BluetoothAdapter.ACTION_DISCOVERY_FINISHED -> {
                    // discovery finished
                }
                BluetoothDevice.ACTION_BOND_STATE_CHANGED -> {
                    // update list item for bond state change
                    val device: BluetoothDevice? = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                    device?.let { d ->
                        val idx = devices.indexOfFirst { it.address == d.address }
                        if (idx >= 0) adapter.notifyItemChanged(idx)
                    }
                }
            }

        }
    }

    interface DeviceActions {
        fun pair(device: BluetoothDevice)
        fun unpair(device: BluetoothDevice)
    }

    class DeviceAdapter(private val items: List<BluetoothDevice>, private val actions: DeviceActions) : RecyclerView.Adapter<DeviceAdapter.VH>() {
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val v = LayoutInflater.from(parent.context).inflate(R.layout.device_item, parent, false)
            return VH(v)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val d = items[position]
            holder.name.text = d.name ?: "Unknown"
            holder.addr.text = d.address
            val bonded = d.bondState == BluetoothDevice.BOND_BONDED
            holder.pairBtn.visibility = if (bonded) View.GONE else View.VISIBLE
            holder.unpairBtn.visibility = if (bonded) View.VISIBLE else View.GONE

            holder.pairBtn.setOnClickListener { actions.pair(d) }
            holder.unpairBtn.setOnClickListener { actions.unpair(d) }
        }

        override fun getItemCount(): Int = items.size

        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val name: TextView = view.findViewById(R.id.tvName)
            val addr: TextView = view.findViewById(R.id.tvAddr)
            val pairBtn: Button = view.findViewById(R.id.btnPair)
            val unpairBtn: Button = view.findViewById(R.id.btnUnpair)
        }
    }
}
