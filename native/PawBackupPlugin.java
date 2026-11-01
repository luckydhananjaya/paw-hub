package com.luckydhananjaya.pawnote;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.provider.DocumentsContract;
import androidx.activity.result.ActivityResult;
import com.getcapacitor.*;
import com.getcapacitor.annotation.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

@CapacitorPlugin(name = "PawBackup")
public class PawBackupPlugin extends Plugin {
    private SharedPreferences prefs() { return getContext().getSharedPreferences("paw_backup", 0); }
    private Uri folder() throws IOException {
        String value = prefs().getString("folder", null);
        if (value == null) throw new IOException("Choose a backup folder first.");
        return Uri.parse(value);
    }
    @PluginMethod public void status(PluginCall call) {
        JSObject result = new JSObject();
        result.put("configured", prefs().contains("folder"));
        call.resolve(result);
    }
    @PluginMethod public void chooseFolder(PluginCall call) {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(call, intent, "folderChosen");
    }
    @ActivityCallback private void folderChosen(PluginCall call, ActivityResult result) {
        if (call == null) return;
        Intent data = result.getData();
        if (result.getResultCode() != Activity.RESULT_OK || data == null || data.getData() == null) {
            call.reject("Folder selection cancelled."); return;
        }
        try {
            Uri uri = data.getData();
            int flags = data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            if ((flags & Intent.FLAG_GRANT_WRITE_URI_PERMISSION) == 0) throw new IOException("Folder is not writable.");
            getContext().getContentResolver().takePersistableUriPermission(uri, flags);
            prefs().edit().putString("folder", uri.toString()).apply();
            call.resolve();
        } catch (Exception e) { call.reject("Could not access this folder. Choose another folder.", e); }
    }
    private List<String[]> files(Uri tree) throws Exception {
        List<String[]> list = new ArrayList<>();
        Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, DocumentsContract.getTreeDocumentId(tree));
        try (Cursor c = getContext().getContentResolver().query(children,
            new String[]{DocumentsContract.Document.COLUMN_DOCUMENT_ID, DocumentsContract.Document.COLUMN_DISPLAY_NAME}, null, null, null)) {
            if (c == null) throw new IOException("Could not read folder.");
            while (c.moveToNext()) {
                String name = c.getString(1);
                if (name != null && name.matches("PawNote-[0-9]+-[a-zA-Z0-9-]+\\.json"))
                    list.add(new String[]{c.getString(0), name});
            }
        }
        list.sort((a,b) -> b[1].compareTo(a[1]));
        return list;
    }
    private String read(Uri uri) throws Exception {
        try (InputStream in = getContext().getContentResolver().openInputStream(uri);
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            if (in == null) throw new IOException("Could not open backup.");
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) != -1) {
                if (out.size() + n > 10 * 1024 * 1024) throw new IOException("Backup is too large.");
                out.write(buf, 0, n);
            }
            return out.toString(StandardCharsets.UTF_8.name());
        }
    }
    @PluginMethod public void write(PluginCall call) {
        getBridge().execute(() -> {
            Uri created = null;
            try {
                String data = call.getString("data");
                if (data == null || data.length() > 5 * 1024 * 1024) throw new IOException("Invalid backup size.");
                new org.json.JSONArray(data);
                Uri tree = folder();
                Uri parent = DocumentsContract.buildDocumentUriUsingTree(tree, DocumentsContract.getTreeDocumentId(tree));
                String name = "PawNote-" + System.currentTimeMillis() + "-" + UUID.randomUUID() + ".json";
                created = DocumentsContract.createDocument(getContext().getContentResolver(), parent, "application/json", name);
                if (created == null) throw new IOException("Could not create backup.");
                try (OutputStream out = getContext().getContentResolver().openOutputStream(created, "wt")) {
                    if (out == null) throw new IOException("Could not write backup.");
                    out.write(data.getBytes(StandardCharsets.UTF_8));
                }
                if (!data.equals(read(created))) throw new IOException("Backup verification failed.");
                // Never prune older backups until the new copy has been read back successfully.
                List<String[]> entries = files(tree);
                for (int i = 20; i < entries.size(); i++) {
                    try { DocumentsContract.deleteDocument(getContext().getContentResolver(),
                        DocumentsContract.buildDocumentUriUsingTree(tree, entries.get(i)[0])); }
                    catch (Exception ignored) {}
                }
                JSObject result = new JSObject();
                result.put("name", name);
                call.resolve(result);
            } catch (Exception e) {
                if (created != null) {
                    try { DocumentsContract.deleteDocument(getContext().getContentResolver(), created); }
                    catch (Exception ignored) {}
                }
                call.reject("Backup failed. Check folder access, connection and available storage.", e);
            }
        });
    }
    @PluginMethod public void list(PluginCall call) {
        getBridge().execute(() -> {
            try {
                JSArray entries = new JSArray();
                for (String[] file : files(folder())) {
                    JSObject item = new JSObject();
                    item.put("id", file[0]); item.put("name", file[1]); entries.put(item);
                }
                JSObject result = new JSObject(); result.put("entries", entries); call.resolve(result);
            } catch (Exception e) { call.reject("Could not list backups. Select the backup folder again.", e); }
        });
    }
    @PluginMethod public void read(PluginCall call) {
        getBridge().execute(() -> {
            try {
                String id = call.getString("id");
                Uri tree = folder();
                boolean found = false;
                for (String[] file : files(tree)) if (file[0].equals(id)) found = true;
                if (!found) throw new IOException("Backup not found.");
                JSObject result = new JSObject();
                result.put("data", read(DocumentsContract.buildDocumentUriUsingTree(tree, id)));
                call.resolve(result);
            } catch (Exception e) { call.reject("Could not read this backup.", e); }
        });
    }
}
