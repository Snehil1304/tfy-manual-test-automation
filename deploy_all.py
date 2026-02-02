import subprocess
import sys
import os
import tempfile
import argparse

# ================= DEFAULT VALUES =================
DEFAULT_CLUSTER = "tfy-usea1-devtest"
DEFAULT_WORKSPACE = "snl-ws"
DEFAULT_BASE_DOMAIN = "tfy-usea1-ctl.devtest.truefoundry.tech"
DEFAULT_EMAIL = "snehil.gajada@truefoundry.com"

DEFAULT_ML_REPO = "snl-ml-repo"
DEFAULT_STORAGE_FQN = "truefoundry:aws:tfy-usea1-ctl-devtest-internal:blob-storage:workflow-test"
DEFAULT_VOLUME = "snl-vol6"

DEFAULT_HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxx"   # Same token is OK
DEFAULT_SECRET_VAL = "mysecret123"
DEFAULT_PASSWORD_SECRET_FQN = "tfy-secret://truefoundry:volume-browser:password"

# 👉 PASTE YOUR SSH PUBLIC KEY HERE
DEFAULT_SSH_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQ...."

# =================================================


def run_command(cmd):
    """Run shell command"""
    result = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        return False, result.stderr or result.stdout
    return True, result.stdout


def apply_templated_yaml(file_path, replacements):
    """Replace placeholders and apply YAML"""
    if not os.path.exists(file_path):
        print(f"[SKIP] File not found: {file_path}")
        return True

    with open(file_path, "r") as f:
        content = f.read()

    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tf:
        tf.write(content)
        temp_file = tf.name

    print(f"\n🚀 Applying {os.path.basename(file_path)}")
    success, output = run_command(f"tfy apply -f {temp_file}")

    os.remove(temp_file)

    if not success:
        print("❌ FAILED")
        print(output)
        return False

    print("✅ SUCCESS")
    return True


def main():
    parser = argparse.ArgumentParser(description="TrueFoundry Manual Test Automation")

    parser.add_argument("--cluster", default=DEFAULT_CLUSTER)
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE)
    parser.add_argument("--email", default=DEFAULT_EMAIL)

    parser.add_argument("--mlrepo", default=DEFAULT_ML_REPO)
    parser.add_argument("--storage-fqn", default=DEFAULT_STORAGE_FQN)
    parser.add_argument("--volume", default=DEFAULT_VOLUME)
    parser.add_argument("--base-domain", default=DEFAULT_BASE_DOMAIN)

    parser.add_argument("--hf-token", default=DEFAULT_HF_TOKEN)
    parser.add_argument("--secret-val", default=DEFAULT_SECRET_VAL)
    parser.add_argument("--password-secret-fqn", default=DEFAULT_PASSWORD_SECRET_FQN)
    parser.add_argument("--ssh-public-key", default=DEFAULT_SSH_PUBLIC_KEY)

    args = parser.parse_args()

    replacements = {
        "CLUSTER_FQN": args.cluster,
        "WORKSPACE_NAME": args.workspace,
        "USER_EMAIL": args.email,
        "ML_REPO_NAME": args.mlrepo,
        "STORAGE_FQN": args.storage_fqn,
        "VOLUME_NAME": args.volume,
        "BASE_DOMAIN": args.base_domain,
        "HF_TOKEN": args.hf_token,
        "MY_SECRET_VAL": args.secret_val,
        "PASSWORD_SECRET_FQN": args.password_secret_fqn,
        "SSH_PUBLIC_KEY": args.ssh_public_key,
    }

    print("\n" + "=" * 60)
    print("🔥 TRUEFOUNDRY MANUAL TEST AUTOMATION STARTED")
    print(f"Cluster   : {args.cluster}")
    print(f"Workspace : {args.workspace}")
    print("=" * 60)

    # ---------- ORDER MATTERS ----------
    infra_files = [
        "yamls/01-ml-repo.yaml",
        "yamls/02-workspace.yaml",
        #"yamls/03-volume.yaml",
    ]

    app_files = [
        "yamls/04-service1.yaml",
        "yamls/05-service2.yaml",
        "yamls/06-service3.yaml",
        "yamls/07-service-autoscale.yaml",
        "yamls/08-llama7b.yaml",
        "yamls/09-notebook.yaml",
        "yamls/10-ssh-server.yaml",
    ]

    for f in infra_files:
        if not apply_templated_yaml(f, replacements):
            print("\n🛑 Infrastructure deployment failed. Exiting.")
            sys.exit(1)

    for f in app_files:
        apply_templated_yaml(f, replacements)

    print("\n" + "=" * 60)
    print("🎉 ALL MANUAL TESTS DEPLOYED SUCCESSFULLY")
    print("Check TF UI → Deployments / Notebooks / SSH / LLM Gateway")
    print("=" * 60)


if __name__ == "__main__":
    main()

