import configparser
import io


def generate_awg_config(
    private_key: str,
    address: str,
    dns: str,
    mtu: int,
    listen_port: int,
    public_key: str,
    endpoint: str,
) -> str:
    """
    Generates an AmneziaWG (AWG 1.5) configuration file.
    """
    config = configparser.ConfigParser()
    config.optionxform = str  # Preserve case for keys

    config["Interface"] = {
        "PrivateKey": private_key,
        "Address": address,
        "DNS": dns,
        "MTU": str(mtu),
        "ListenPort": str(listen_port),
    }

    config["Peer"] = {
        "PublicKey": public_key,
        "Endpoint": endpoint,
        "AllowedIPs": "0.0.0.0/0",
    }

    with io.StringIO() as string_writer:
        config.write(string_writer)
        return string_writer.getvalue()
