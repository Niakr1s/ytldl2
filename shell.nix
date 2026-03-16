{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    zlib
    libjpeg
    libwebp
    pkg-config # Helps build systems find libraries
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.zlib}/lib:$LD_LIBRARY_PATH"
    export LIBRARY_PATH="${pkgs.zlib}/lib:$LIBRARY_PATH"
    export C_INCLUDE_PATH="${pkgs.zlib}/include:$C_INCLUDE_PATH"
  '';
}
