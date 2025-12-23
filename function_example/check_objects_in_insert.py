"""
unit이 '알람존' ObjectType의 범위 안에 들어왔는지 확인하는 함수
"""


def check_objects_in_alert():
    from graphio_sdk import GraphioClient
    client = GraphioClient()

    try:
        Unit = client.ontology.get_object_type("유닛")
        Zone = client.ontology.get_object_type("지역")

        if not Unit:
            raise ValueError("'유닛' ObjectType을 찾을 수 없습니다.")

        # 조회 쿼리 구성
        unit_query = Unit.select('side', 'y', 'x')
        zone_query = Zone.select()

        # 데이터 조회
        units = unit_query.execute()
        zones = zone_query.execute()

        if not units:
            print("체크할 '유닛' 데이터가 없습니다.")
            return {
                "updated_count": 0,
                "results": None
            }

        print(f"조회된 '유닛' 데이터: {len(units)}건")

        for unit in units:
            props = unit.get('properties')

            if props.get('side') == 'ALLY':
                continue

            x = props.get('x')
            y = props.get('y')

            # x, y 좌표가 없는 경우 건너뛰기
            if x is None or y is None:
                continue

            for z in zones:
                zone_props = z.get("properties", {})
                lx = zone_props.get("lx")
                ly = zone_props.get("ly")
                rx = zone_props.get("rx")
                ry = zone_props.get("ry")

                # 좌표 범위 확인
                if lx is not None and ly is not None and rx is not None and ry is not None:
                    if lx <= x <= rx and ly <= y <= ry:
                        return True
        return False
    except Exception as e:
        print(f"[check_objects_in_danger_zone] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        client.close()


if __name__ == "__main__":
    """
    사용 예제
    """
    check_objects_in_alert()
